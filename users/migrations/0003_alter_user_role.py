# Generated by Django 3.2.25 on 2025-03-23 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('cleaner', 'Cleaner'), ('supervisor', 'Supervisor'), ('senior supervisor', 'Senior Supervisor'), ('room attendee', 'Room Attendee'), ('admin', 'Admin'), ('staff', 'Staff'), ('hotel-contact-person', 'Hotel Contact Person')], default='staff', max_length=20),
        ),
    ]
