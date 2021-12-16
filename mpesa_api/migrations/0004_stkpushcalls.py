# Generated by Django 4.0 on 2021-12-15 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0003_delete_stkpushcalls'),
    ]

    operations = [
        migrations.CreateModel(
            name='StkPushCalls',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('transactionType', models.CharField(max_length=225)),
                ('amount', models.IntegerField()),
                ('partyA', models.CharField(max_length=225)),
                ('partyB', models.CharField(max_length=255)),
                ('phoneNumber', models.CharField(max_length=255)),
                ('accountReference', models.CharField(max_length=255)),
                ('transactionDesc', models.CharField(max_length=255)),
                ('merchantRequestId', models.CharField(max_length=255)),
                ('checkoutRequestId', models.CharField(max_length=255)),
                ('responseCode', models.CharField(max_length=255)),
                ('responseDescription', models.CharField(max_length=255)),
                ('customerMessage', models.CharField(max_length=255)),
            ],
        ),
    ]
