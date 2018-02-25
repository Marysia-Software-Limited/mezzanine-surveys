# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import mezzanine.core.fields
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', mezzanine.core.fields.RichTextField(verbose_name='Description')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('field_type', models.IntegerField(verbose_name='Question type', choices=[(1, 'Rating'), (2, 'Text')])),
                ('prompt', models.CharField(max_length=300, verbose_name='Prompt')),
                ('invert_rating', models.BooleanField(default=False, help_text='If checked the rating given will be inverted', verbose_name='Invert rating')),
                ('max_rating', models.PositiveSmallIntegerField(default=5, help_text='Must be a number between 2 and 10', verbose_name='Maximum rating', validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(10)])),
                ('required', models.BooleanField(default=True, verbose_name='Required')),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prompt', models.CharField(max_length=200, verbose_name='Prompt')),
                ('rating', models.PositiveSmallIntegerField(null=True, verbose_name='Rating', blank=True)),
                ('text_response', models.TextField(verbose_name='Text response', blank=True)),
                ('question', models.ForeignKey(to='surveys.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_order', mezzanine.core.fields.OrderField(null=True, verbose_name='Order')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', mezzanine.core.fields.RichTextField(verbose_name='Description')),
                ('category', models.ForeignKey(related_name='subcategories', to='surveys.Category')),
            ],
            options={
                'ordering': ['category', '_order'],
                'verbose_name': 'subcategory',
                'verbose_name_plural': 'subcategories',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('instructions', mezzanine.core.fields.RichTextField(verbose_name='Instructions')),
                ('cost', models.DecimalField(verbose_name='Cost', max_digits=7, decimal_places=2)),
                ('purchase_response', mezzanine.core.fields.RichTextField(verbose_name='Purchase response')),
                ('completed_message', mezzanine.core.fields.RichTextField(help_text='Message shown to users after completing the survey', verbose_name='Completed message')),
                ('report_explanation', mezzanine.core.fields.RichTextField(help_text="Helping content shown before the results' detail", verbose_name='Explanation')),
            ],
            options={
                'ordering': ('_order',),
                'verbose_name': 'survey',
                'verbose_name_plural': 'surveys',
            },
            bases=('pages.page', models.Model),
        ),
        migrations.CreateModel(
            name='SurveyPurchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('public_id', models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)),
                ('billing_zipcode', models.CharField(max_length=20, verbose_name='Billing Zipcode')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('email', models.EmailField(max_length=300, verbose_name='Email')),
                ('transaction_id', models.CharField(max_length=200, verbose_name='Transaction ID', blank=True)),
                ('charge_details', models.TextField(verbose_name='Charge details', blank=True)),
                ('report_generated', models.DateTimeField(null=True, verbose_name='Report generated', blank=True)),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
            },
        ),
        migrations.CreateModel(
            name='SurveyPurchaseCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text='If left blank it will be automatically generated', max_length=20, verbose_name='Code', blank=True)),
                ('uses_remaining', models.IntegerField(default=0)),
                ('survey', models.ForeignKey(related_name='codes', to='surveys.Survey')),
            ],
            options={
                'verbose_name': 'purchase code',
                'verbose_name_plural': 'purchase codes',
            },
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='purchased_with_code',
            field=models.ForeignKey(blank=True, to='surveys.SurveyPurchaseCode', null=True),
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='purchaser',
            field=models.ForeignKey(related_name='surveys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='survey',
            field=models.ForeignKey(related_name='purchases', to='surveys.Survey'),
        ),
        migrations.AddField(
            model_name='question',
            name='subcategory',
            field=models.ForeignKey(related_name='questions', blank=True, to='surveys.Subcategory', null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(related_name='questions', to='surveys.Survey'),
        ),
        migrations.AlterUniqueTogether(
            name='surveypurchasecode',
            unique_together=set([('survey', 'code')]),
        ),
    ]
