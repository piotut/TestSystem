# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_number', models.SmallIntegerField()),
                ('a_points', models.SmallIntegerField(null=True)),
                ('b_points', models.SmallIntegerField(null=True)),
                ('c_points', models.SmallIntegerField(null=True)),
                ('d_points', models.SmallIntegerField(null=True)),
                ('e_points', models.SmallIntegerField(null=True)),
                ('f_points', models.SmallIntegerField(null=True)),
            ],
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
                ('question_id', models.ForeignKey(to='testownik.Question')),
            ],
        ),
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sheet_number', models.SmallIntegerField()),
                ('points', models.SmallIntegerField(null=True)),
            ],
            options={
                'verbose_name': 'Arkusz',
                'verbose_name_plural': 'Arkusze',
            },
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
                'verbose_name_plural': 'Studenci',
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('time', models.SmallIntegerField(null=True)),
            ],
            options={
                'verbose_name': 'Test',
                'verbose_name_plural': 'Testy',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_teacher', models.BooleanField(default=False)),
                ('is_supervisor', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil u\u017cytkownika',
                'verbose_name_plural': 'Profile u\u017cytkownik\xf3w',
            },
        ),
        migrations.AddField(
            model_name='test',
            name='author_id',
            field=models.ForeignKey(to='testownik.UserProfile'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='student_id',
            field=models.ForeignKey(to='testownik.Student'),
        ),
        migrations.AddField(
            model_name='sheet',
            name='test_id',
            field=models.ForeignKey(to='testownik.Test'),
        ),
        migrations.AddField(
            model_name='results',
            name='sheet_id',
            field=models.ForeignKey(to='testownik.Sheet'),
        ),
    ]
