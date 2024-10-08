# Generated by Django 5.0.7 on 2024-09-08 15:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_billinginfo_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billinginfo',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.cartorder'),
        ),
        migrations.AlterField(
            model_name='shippinginfo',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.cartorder'),
        ),
    ]
