# Generated by Django 4.0 on 2021-12-15 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0007_stkpushcalls_paymentstatus_stkpushcalls_stkstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stkpushcalls',
            name='paymentStatus',
            field=models.CharField(default='Pending', max_length=255),
        ),
        migrations.AlterField(
            model_name='stkpushcalls',
            name='stkStatus',
            field=models.CharField(default='Success', max_length=255),
        ),
    ]
