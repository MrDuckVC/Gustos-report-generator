# Generated by Django 4.1.5 on 2023-06-06 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['updated'], name='generator_t_updated_d63c8f_idx'),
        ),
    ]