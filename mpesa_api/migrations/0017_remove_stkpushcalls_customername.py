# Generated by Django 4.0 on 2022-01-10 09:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0016_stkpushcalls_first_name_stkpushcalls_last_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stkpushcalls',
            name='customerName',
        ),
    ]
