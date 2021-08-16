# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-18 17:11
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bag_transfer', '0003_auto_20180502_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractExternalIdentifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(choices=[('archivesspace', 'ArchivesSpace'), ('aurora', 'Aurora'), ('archivematica', 'Archivematica'), ('fedora', 'Fedora')], max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='accession',
            name='created',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='accession',
            name='language',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bag_transfer.LanguageCode'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accession',
            name='last_modified',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accession',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accession', to='bag_transfer.Organization'),
        ),
        migrations.AddField(
            model_name='archives',
            name='accession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accession_transfers', to='bag_transfer.Accession'),
        ),
        migrations.AddField(
            model_name='recordcreators',
            name='type',
            field=models.CharField(choices=[('family', 'Family'), ('organization', 'Organization'), ('person', 'Person')], default='organization', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='accession',
            name='creators',
            field=models.ManyToManyField(blank=True, to='bag_transfer.RecordCreators'),
        ),
        migrations.AlterField(
            model_name='baglog',
            name='archive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='bag_transfer.Archives'),
        ),
        migrations.AlterField(
            model_name='rightsstatement',
            name='accession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rights_statements', to='bag_transfer.Accession'),
        ),
        migrations.CreateModel(
            name='AccessionExternalIdentifier',
            fields=[
                ('abstractexternalidentifier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bag_transfer.AbstractExternalIdentifier')),
                ('accession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_identifier', to='bag_transfer.Accession')),
            ],
            bases=('bag_transfer.abstractexternalidentifier',),
        ),
        migrations.CreateModel(
            name='ArchiveExternalIdentifier',
            fields=[
                ('abstractexternalidentifier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bag_transfer.AbstractExternalIdentifier')),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='external_identifier', to='bag_transfer.Archives')),
            ],
            bases=('bag_transfer.abstractexternalidentifier',),
        ),
        migrations.CreateModel(
            name='CollectionExternalIdentifier',
            fields=[
                ('abstractexternalidentifier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bag_transfer.AbstractExternalIdentifier')),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collection_identifier', to='bag_transfer.Archives')),
            ],
            bases=('bag_transfer.abstractexternalidentifier',),
        ),
        migrations.CreateModel(
            name='ParentExternalIdentifier',
            fields=[
                ('abstractexternalidentifier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bag_transfer.AbstractExternalIdentifier')),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_identifier', to='bag_transfer.Archives')),
            ],
            bases=('bag_transfer.abstractexternalidentifier',),
        ),
    ]
