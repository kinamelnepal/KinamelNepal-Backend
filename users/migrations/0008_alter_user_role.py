# Generated by Django 3.2.25 on 2025-04-30 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('buyer', 'Buyer'), ('seller', 'Seller'), ('admin', 'Admin')], max_length=20),
        ),
    ]
