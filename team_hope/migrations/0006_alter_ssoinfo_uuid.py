# Generated by Django 5.0.4 on 2024-05-28 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_hope', '0005_ssoinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ssoinfo',
            name='uuid',
            field=models.CharField(max_length=32, null=True, unique=True),
        ),
    ]
