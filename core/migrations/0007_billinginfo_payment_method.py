# Generated by Django 5.0.7 on 2024-09-08 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_billinginfo_user_remove_shippinginfo_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='billinginfo',
            name='payment_method',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
