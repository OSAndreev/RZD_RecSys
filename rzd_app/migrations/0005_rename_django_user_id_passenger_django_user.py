# Generated by Django 3.2.22 on 2023-10-13 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rzd_app', '0004_passenger_django_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passenger',
            old_name='django_user_id',
            new_name='django_user',
        ),
    ]