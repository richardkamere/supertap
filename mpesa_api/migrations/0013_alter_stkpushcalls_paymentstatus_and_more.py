# Generated by Django 4.0 on 2022-01-06 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0012_alter_stkpushcalls_paymentstatus_and_more'),
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
            field=models.CharField(default='Failed', max_length=255),
        ),
    ]