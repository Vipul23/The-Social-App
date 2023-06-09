# Generated by Django 4.2 on 2023-05-05 13:22

from django.db import migrations, models
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0007_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profileimg',
            field=models.ImageField(default='profile_default.jpg', upload_to=social.models.profileimage_saver),
        ),
    ]
