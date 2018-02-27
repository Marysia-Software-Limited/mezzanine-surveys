# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid
from django.conf import settings
import mezzanine.core.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20150527_1555'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('_order', mezzanine.core.fields.OrderField(verbose_name='Order', null=True)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('description', mezzanine.core.fields.RichTextField(verbose_name='Description')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('_order', mezzanine.core.fields.OrderField(verbose_name='Order', null=True)),
                ('field_type', models.IntegerField(verbose_name='Question type', choices=[(1, 'Rating'), (2, 'Text')])),
                ('prompt', models.CharField(verbose_name='Prompt', max_length=300)),
                ('invert_rating', models.BooleanField(verbose_name='Invert rating', default=False, help_text='If checked the rating given will be inverted')),
                ('max_rating', models.PositiveSmallIntegerField(verbose_name='Maximum rating', default=5, help_text='Must be a number between 2 and 10', validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(10)])),
                ('required', models.BooleanField(verbose_name='Required', default=True)),
            ],
            options={
                'ordering': ('_order',),
            },
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('rating', models.PositiveSmallIntegerField(verbose_name='Rating', blank=True, null=True)),
                ('text_response', models.TextField(verbose_name='Text response', blank=True)),
                ('question', models.ForeignKey(related_name='responses', to='surveys.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('_order', mezzanine.core.fields.OrderField(verbose_name='Order', null=True)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('description', mezzanine.core.fields.RichTextField(verbose_name='Description')),
                ('category', models.ForeignKey(related_name='subcategories', to='surveys.Category')),
            ],
            options={
                'verbose_name': 'subcategory',
                'verbose_name_plural': 'subcategories',
                'ordering': ['category', '_order'],
            },
        ),
        migrations.CreateModel(
            name='SurveyPage',
            fields=[
                ('page_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='pages.Page')),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('instructions', mezzanine.core.fields.RichTextField(verbose_name='Instructions')),
                ('cost', models.DecimalField(verbose_name='Cost', max_digits=7, decimal_places=2)),
                ('purchase_response', mezzanine.core.fields.RichTextField(verbose_name='Purchase response')),
                ('completed_message', mezzanine.core.fields.RichTextField(verbose_name='Completed message', help_text='Message shown to users after completing the survey')),
                ('report_explanation', mezzanine.core.fields.RichTextField(verbose_name='Explanation', help_text="Helping content shown before the results' detail")),
            ],
            options={
                'verbose_name': 'survey page',
                'verbose_name_plural': 'survey pages',
                'ordering': ('_order',),
            },
            bases=('pages.page', models.Model),
        ),
        migrations.CreateModel(
            name='SurveyPurchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('public_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('email', models.EmailField(verbose_name='Email', max_length=300)),
                ('transaction_id', models.CharField(verbose_name='Transaction ID', max_length=200, blank=True)),
                ('charge_details', models.TextField(verbose_name='Charge details', blank=True)),
                ('report_generated', models.DateTimeField(verbose_name='Report generated', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
            },
        ),
        migrations.CreateModel(
            name='SurveyPurchaseCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code', max_length=20, blank=True, help_text='If left blank it will be automatically generated')),
                ('uses_remaining', models.PositiveIntegerField(verbose_name='Remaining uses', default=0)),
                ('survey', models.ForeignKey(related_name='purchase_codes', to='surveys.SurveyPage')),
            ],
            options={
                'verbose_name': 'purchase code',
                'verbose_name_plural': 'purchase codes',
            },
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='purchased_with_code',
            field=models.ForeignKey(blank=True, null=True, to='surveys.SurveyPurchaseCode'),
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='purchaser',
            field=models.ForeignKey(related_name='surveys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='surveypurchase',
            name='survey',
            field=models.ForeignKey(related_name='purchases', to='surveys.SurveyPage'),
        ),
        migrations.AddField(
            model_name='question',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, related_name='questions', to='surveys.Subcategory'),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(related_name='questions', to='surveys.SurveyPage'),
        ),
        migrations.AlterUniqueTogether(
            name='surveypurchasecode',
            unique_together=set([('survey', 'code')]),
        ),
    ]
