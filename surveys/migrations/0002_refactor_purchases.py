# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surveypurchase',
            name='charge_details',
        ),
        migrations.RemoveField(
            model_name='surveypurchase',
            name='email',
        ),
        migrations.RemoveField(
            model_name='surveypurchase',
            name='name',
        ),
        migrations.RemoveField(
            model_name='surveypurchase',
            name='purchased_with_code',
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='amount',
            field=models.DecimalField(verbose_name='Amount', blank=True, null=True, max_digits=8, decimal_places=2),
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='notes',
            field=models.TextField(verbose_name='Notes', blank=True),
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='payment_method',
            field=models.CharField(verbose_name='Payment method', max_length=100, blank=True),
        ),
    ]
