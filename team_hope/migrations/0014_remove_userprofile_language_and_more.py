# Generated by Django 5.0.7 on 2024-09-02 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_hope', '0013_userprofile_ethnicity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='language',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='primary_language',
            field=models.CharField(blank=True, choices=[('English', 'English'), ('Spanish', 'Spanish'), ('French', 'French'), ('German', 'German'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese'), ('Hindi', 'Hindi'), ('Arabic', 'Arabic'), ('Portuguese', 'Portuguese'), ('Russian', 'Russian'), ('Other', 'Other')], default='English', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='secondary_language',
            field=models.CharField(blank=True, choices=[('English', 'English'), ('Spanish', 'Spanish'), ('French', 'French'), ('German', 'German'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese'), ('Hindi', 'Hindi'), ('Arabic', 'Arabic'), ('Portuguese', 'Portuguese'), ('Russian', 'Russian'), ('Other', 'Other'), ('None', 'None')], default='None', max_length=100, null=True),
        ),
    ]
