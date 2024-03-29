# Generated by Django 2.2.5 on 2019-11-18 11:25

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('List_Type', models.CharField(choices=[('OL', 'Numbered List'), ('UL', 'List')], default='UL', max_length=2)),
                ('icon', models.URLField(default='http://', help_text='Enter Image Link')),
                ('category', models.CharField(max_length=500)),
            ],
            options={
                'ordering': ['category'],
            },
        ),
        migrations.CreateModel(
            name='Countries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Country_code', models.CharField(max_length=2)),
                ('Country_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Info', models.CharField(max_length=250)),
                ('Image_url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sub_Categories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category', models.CharField(max_length=100)),
                ('Sub_Category', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Websites',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Number', models.IntegerField(blank=True, null=True)),
                ('url', models.URLField(default='http://')),
                ('website', models.CharField(default='None', max_length=250)),
                ('Countries', models.ManyToManyField(blank=True, null=True, to='Websites.Countries')),
                ('Tags', models.ManyToManyField(blank=True, null=True, related_name='Tags', to='Websites.Sub_Categories')),
                ('category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='websites', to='Websites.Categories')),
            ],
            options={
                'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('category'), nulls_last=True), 'category', django.db.models.expressions.OrderBy(django.db.models.expressions.F('Number'), nulls_last=True)],
            },
        ),
        migrations.AddField(
            model_name='categories',
            name='sub_categories',
            field=models.ManyToManyField(related_name='sub_categories', to='Websites.Sub_Categories'),
        ),
    ]
