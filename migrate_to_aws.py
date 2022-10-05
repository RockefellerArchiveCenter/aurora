import os

import boto3
from asterism.bagit_helpers import update_bag_info
from asterism.file_helpers import make_tarfile, remove_file_or_dir
from django.conf import settings

from bag_transfer.models import Organization, Transfer, User


def validate_orgs():
    """Ensures that orgs have at least one admin user and S3 credentials."""
    for org in Organization.objects.filter(is_active=True):
        if settings.S3_USE:
            assert len(org.admin_users) > 0
            if not all([org.s3_username, org.s3_access_key_id, org.s3_secret_access_key]):
                bucket = org.create_s3_bucket()
                org.s3_access_key_id, org.s3_secret_access_key, org.s3_username = org.create_iam_user(bucket)
                org.save()


def move_files_to_s3():
    """Moves files in local storage directory to storage bucket"""
    if settings.S3_USE:
        for filename in os.listdir(settings.STORAGE_DIR):
            local_filepath = os.join(settings.STORAGE_DIR, filename)
            transfer_obj = Transfer.objects.get(machine_file_path=local_filepath)
            update_bag_info(local_filepath, {"Origin": "aurora"})
            tar_filename = f"{filename}.tar.gz"
            local_tarpath = os.path.join(settings.STORAGE_DIR, tar_filename)
            make_tarfile(local_filepath, local_tarpath)
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION)
            s3_client.upload_file(local_tarpath, settings.STORAGE_BUCKET, tar_filename)
            transfer_obj.machine_file_path = tar_filename
            transfer_obj.save()
            remove_file_or_dir(local_tarpath)
            remove_file_or_dir(local_filepath)


def reset_user_passwords():
    """Reset passwords for all users."""
    for user in User.objects.filter(is_active=True):
        if settings.COGNITO_USE:
            cognito_client = boto3.client(
                'cognito-idp',
                aws_access_key_id=settings.COGNITO_ACCESS_KEY,
                aws_secret_access_key=settings.COGNITO_SECRET_KEY,
                region_name=settings.COGNITO_REGION)
            user.create_cognito_user(cognito_client)
            if not settings.S3_USE:
                user.create_system_user()
                user.add_user_to_system_group()


def main():
    validate_orgs()
    move_files_to_s3()
    reset_user_passwords()


if __name__ == "__main__":
    main()
