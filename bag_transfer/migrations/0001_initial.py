# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-25 14:14
from __future__ import unicode_literals

import datetime

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_machine_account', models.BooleanField(default=True)),
                ('from_ldap', models.BooleanField(default=False)),
                ('is_new_account', models.BooleanField(default=False)),
                ('is_org_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'ordering': ['username'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AcceptBagItVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('0.96', '0.96'), ('0.97', '0.97')], max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='AcceptSerialization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('application/zip', 'application/zip'), ('application/x-tar', 'application/x-tar'), ('application/x-gzip', 'application/x-gzip')], max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('accession_number', models.CharField(max_length=10)),
                ('accession_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('extent_files', models.PositiveIntegerField()),
                ('extent_size', models.PositiveIntegerField()),
                ('description', models.TextField()),
                ('access_restrictions', models.TextField()),
                ('use_restrictions', models.TextField()),
                ('resource', models.URLField()),
                ('acquisition_type', models.CharField(max_length=200)),
                ('appraisal_note', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Archives',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_file_path', models.CharField(max_length=100)),
                ('machine_file_size', models.CharField(max_length=30)),
                ('machine_file_upload_time', models.DateTimeField()),
                ('machine_file_identifier', models.CharField(max_length=255, unique=True)),
                ('machine_file_type', models.CharField(choices=[('ZIP', 'zip'), ('TAR', 'tar'), ('OTHER', 'OTHER')], max_length=5)),
                ('bag_it_name', models.CharField(max_length=60)),
                ('bag_it_valid', models.BooleanField(default=False)),
                ('appraisal_note', models.TextField(blank=True, null=True)),
                ('additional_error_info', models.CharField(blank=True, max_length=255, null=True)),
                ('process_status', models.PositiveSmallIntegerField(choices=[(10, 'Transfer Started'), (20, 'Transfer Completed'), (30, 'Invalid'), (40, 'Validated'), (60, 'Rejected'), (70, 'Accepted'), (75, 'Accessioning Started'), (90, 'Accession Complete')], default=20)),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('modified_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['machine_file_upload_time'],
            },
        ),
        migrations.CreateModel(
            name='BagInfoMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_identifier', models.CharField(max_length=256)),
                ('internal_sender_description', models.TextField()),
                ('title', models.CharField(max_length=256)),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
                ('record_type', models.CharField(max_length=30)),
                ('bagging_date', models.DateTimeField()),
                ('bag_count', models.CharField(max_length=10)),
                ('bag_group_identifier', models.CharField(max_length=256)),
                ('payload_oxum', models.CharField(max_length=20)),
                ('bagit_profile_identifier', models.URLField()),
                ('archive', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='bag_transfer.Archives')),
            ],
        ),
        migrations.CreateModel(
            name='BagItProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_descripton', models.TextField(blank=True)),
                ('version', models.DecimalField(decimal_places=1, default=0.0, max_digits=4)),
                ('bagit_profile_identifier', models.URLField(blank=True)),
                ('contact_email', models.EmailField(max_length=254)),
                ('allow_fetch', models.BooleanField(default=False)),
                ('serialization', models.CharField(choices=[('forbidden', 'forbidden'), ('required', 'required'), ('optional', 'optional')], default='optional', max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='BagItProfileBagInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(choices=[('source_organization', 'Source-Organization'), ('organization_address', 'Organization-Address'), ('contact_name', 'Contact-Name'), ('contact_phone', 'Contact-Phone'), ('contact_email', 'Contact-Email'), ('external_descripton', 'External-Description'), ('external_identifier', 'External-Identifier'), ('internal_sender_description', 'Internal-Sender-Description'), ('internal_sender_identifier', 'Internal-Sender-Identifier'), ('title', 'Title'), ('date_start', 'Date-Start'), ('date_end', 'Date-End'), ('record_creators', 'Record-Creators'), ('record_type', 'Record-Type'), ('language', 'Language'), ('bagging_date', 'Bagging-Date'), ('bag_group_identifier', 'Bag-Group-Identifier'), ('bag_count', 'Bag-Count'), ('bag_size', 'Bag-Size'), ('payload_oxum', 'Payload-Oxum')], max_length=100)),
                ('required', models.NullBooleanField(default=False)),
                ('repeatable', models.NullBooleanField(default=True)),
                ('bagit_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.BagItProfile')),
            ],
        ),
        migrations.CreateModel(
            name='BagItProfileBagInfoValues',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('bagit_profile_baginfo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.BagItProfileBagInfo')),
            ],
        ),
        migrations.CreateModel(
            name='BAGLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_info', models.CharField(blank=True, max_length=255, null=True)),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('archive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='bag_transfer.Archives')),
            ],
            options={
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='BAGLogCodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_short', models.CharField(max_length=5)),
                ('code_type', models.CharField(choices=[('BE', 'Bag Error'), ('GE', 'General Error'), ('I', 'Info'), ('S', 'Success')], max_length=15)),
                ('code_desc', models.CharField(max_length=60)),
                ('next_action', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='ManifestsRequired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('sha256', 'sha256'), ('md5', 'md5')], max_length=20)),
                ('bagit_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manifests_required', to='bag_transfer.BagItProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=60, unique=True)),
                ('machine_name', models.CharField(default='orgXXX will be created here', max_length=30, unique=True)),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('modified_time', models.DateTimeField(auto_now_add=True)),
                ('acquisition_type', models.CharField(blank=True, choices=[('donation', 'Donation'), ('deposit', 'Deposit'), ('transfer', 'Transfer')], max_length=25, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RecordCreators',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RecordType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RightsStatement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rights_basis', models.CharField(choices=[('Copyright', 'Copyright'), ('Statute', 'Statute'), ('License', 'License'), ('Other', 'Other')], max_length=64)),
                ('accession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.Accession')),
                ('applies_to_type', models.ManyToManyField(to='bag_transfer.RecordType')),
                ('archive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.Archives')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='RightsStatementCopyright',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('copyright_status', models.CharField(choices=[('copyrighted', 'copyrighted'), ('public domain', 'public domain'), ('unknown', 'unknown')], default='unknown', max_length=64)),
                ('copyright_jurisdiction', models.CharField(default='us', max_length=2)),
                ('copyright_status_determination_date', models.DateField(blank=True, default=datetime.datetime.now, null=True)),
                ('copyright_applicable_start_date', models.DateField(blank=True, null=True)),
                ('copyright_applicable_end_date', models.DateField(blank=True, null=True)),
                ('copyright_start_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('copyright_end_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('copyright_end_date_open', models.BooleanField(default=False)),
                ('copyright_note', models.TextField()),
                ('rights_statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.RightsStatement')),
            ],
        ),
        migrations.CreateModel(
            name='RightsStatementLicense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_terms', models.TextField(blank=True, null=True)),
                ('license_applicable_start_date', models.DateField(blank=True, null=True)),
                ('license_applicable_end_date', models.DateField(blank=True, null=True)),
                ('license_start_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('license_end_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('license_end_date_open', models.BooleanField(default=False)),
                ('license_note', models.TextField()),
                ('rights_statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.RightsStatement')),
            ],
        ),
        migrations.CreateModel(
            name='RightsStatementOther',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('other_rights_basis', models.CharField(choices=[('Donor', 'Donor'), ('Policy', 'Policy')], max_length=64)),
                ('other_rights_applicable_start_date', models.DateField(blank=True, null=True)),
                ('other_rights_applicable_end_date', models.DateField(blank=True, null=True)),
                ('other_rights_start_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('other_rights_end_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('other_rights_end_date_open', models.BooleanField(default=False)),
                ('other_rights_note', models.TextField()),
                ('rights_statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.RightsStatement')),
            ],
        ),
        migrations.CreateModel(
            name='RightsStatementRightsGranted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('act', models.CharField(choices=[('publish', 'Publish'), ('disseminate', 'Disseminate'), ('replicate', 'Replicate'), ('migrate', 'Migrate'), ('modify', 'Modify'), ('use', 'Use'), ('delete', 'Delete')], max_length=64)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('start_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('end_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('end_date_open', models.BooleanField(default=False)),
                ('rights_granted_note', models.TextField()),
                ('restriction', models.CharField(choices=[('allow', 'Allow'), ('disallow', 'Disallow'), ('conditional', 'Conditional')], max_length=64)),
                ('rights_statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.RightsStatement')),
            ],
        ),
        migrations.CreateModel(
            name='RightsStatementStatute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statute_jurisdiction', models.CharField(default='us', max_length=2)),
                ('statute_citation', models.TextField()),
                ('statute_determination_date', models.DateField(blank=True, null=True)),
                ('statute_applicable_start_date', models.DateField(blank=True, null=True)),
                ('statute_applicable_end_date', models.DateField(blank=True, null=True)),
                ('statute_start_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('statute_end_date_period', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('statute_end_date_open', models.BooleanField(default=False)),
                ('statute_note', models.TextField()),
                ('rights_statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.RightsStatement')),
            ],
        ),
        migrations.CreateModel(
            name='TagFilesRequired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('bagit_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.BagItProfile')),
            ],
        ),
        migrations.CreateModel(
            name='TagManifestsRequired',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('sha256', 'sha256'), ('md5', 'md5')], max_length=20)),
                ('bagit_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.BagItProfile')),
            ],
        ),
        migrations.AddField(
            model_name='baglog',
            name='code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.BAGLogCodes'),
        ),
        migrations.AddField(
            model_name='bagitprofile',
            name='applies_to_organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applies_to_organization', to='bag_transfer.Organization'),
        ),
        migrations.AddField(
            model_name='bagitprofile',
            name='source_organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_organization', to='bag_transfer.Organization'),
        ),
        migrations.AddField(
            model_name='baginfometadata',
            name='language',
            field=models.ManyToManyField(blank=True, to='bag_transfer.LanguageCode'),
        ),
        migrations.AddField(
            model_name='baginfometadata',
            name='record_creators',
            field=models.ManyToManyField(blank=True, to='bag_transfer.RecordCreators'),
        ),
        migrations.AddField(
            model_name='baginfometadata',
            name='source_organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.Organization'),
        ),
        migrations.AddField(
            model_name='archives',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='bag_transfer.Organization'),
        ),
        migrations.AddField(
            model_name='archives',
            name='user_uploaded',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='accession',
            name='creators',
            field=models.ManyToManyField(to='bag_transfer.RecordCreators'),
        ),
        migrations.AddField(
            model_name='acceptserialization',
            name='bagit_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accept_serialization', to='bag_transfer.BagItProfile'),
        ),
        migrations.AddField(
            model_name='acceptbagitversion',
            name='bagit_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.BagItProfile'),
        ),
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.Organization'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
