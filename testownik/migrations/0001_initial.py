# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a_points', models.SmallIntegerField()),
                ('b_points', models.SmallIntegerField()),
                ('c_points', models.SmallIntegerField()),
                ('d_points', models.SmallIntegerField()),
                ('e_points', models.SmallIntegerField()),
                ('f_points', models.SmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('a', models.BooleanField()),
                ('b', models.BooleanField()),
                ('c', models.BooleanField()),
                ('d', models.BooleanField()),
                ('e', models.BooleanField()),
                ('f', models.BooleanField()),
                ('question_id', models.OneToOneField(to='testownik.Question')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SheetQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_number', models.IntegerField()),
                ('answer_order', models.CharField(max_length=6)),
                ('question_id', models.ForeignKey(to='testownik.Question')),
                ('sheet_id', models.ForeignKey(to='testownik.Sheet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('index_number', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('author_id', models.ForeignKey(to='testownik.Teacher')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sheet',
            name='student_id',
            field=models.ForeignKey(to='testownik.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sheet',
            name='test_id',
            field=models.ForeignKey(to='testownik.Test'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='results',
            name='sheet_id',
            field=models.ForeignKey(to='testownik.Sheet'),
            preserve_default=True,
        ),
    ]
