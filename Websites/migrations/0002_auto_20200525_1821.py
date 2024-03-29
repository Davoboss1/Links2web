# Generated by Django 3.0.3 on 2020-05-25 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Websites', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='icon',
            field=models.ImageField(blank=True, help_text='Select image to upload', null=True, upload_to='categories'),
        ),
        migrations.AlterField(
            model_name='categories',
            name='sub_categories',
            field=models.ManyToManyField(related_name='categories', to='Websites.Sub_Categories'),
        ),
    ]
