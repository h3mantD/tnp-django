# Generated by Django 3.1.4 on 2020-12-14 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tnpPortal', '0008_auto_20201214_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companydata',
            name='cname',
            field=models.CharField(max_length=100),
        ),
    ]
