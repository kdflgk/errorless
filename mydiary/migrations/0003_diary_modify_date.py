# Generated by Django 3.1.3 on 2021-03-03 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mydiary', '0002_diary_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='diary',
            name='modify_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
