# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_teacher = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)

    def __unicode__(self):
        return "{}".format(self.user.username)

    class Meta:
        verbose_name = u"Profil użytkownika"
        verbose_name_plural = u"Profile użytkowników"


class Student(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    index_number = models.IntegerField()

    def __unicode__(self):
        return u"{} {}: {}".format(self.first_name, self.last_name, self.index_number)

    class Meta:
        verbose_name_plural = "Studenci"


class Question(models.Model):
    question_number = models.SmallIntegerField()
    a_points = models.SmallIntegerField(null=True)
    b_points = models.SmallIntegerField(null=True)
    c_points = models.SmallIntegerField(null=True)
    d_points = models.SmallIntegerField(null=True)
    e_points = models.SmallIntegerField(null=True)
    f_points = models.SmallIntegerField(null=True)


class Test(models.Model):
    name = models.CharField(max_length=100, default='')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    author_id = models.ForeignKey(UserProfile)
    time = models.SmallIntegerField(null=True)

    def __unicode__(self):
        return "{}, {}".format(self.name, self.author_id)

    def is_active(self):
        return self.end_time > timezone.now() > self.start_time 

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testy"


class SheetManager(models.Manager):

    def get_test_and_sheet_number(self, student_index):
        '''zwraca obiekt testu oraz numer arkusza w danym teście'''
        query = self.filter(student_id__index_number=student_index)
        for qs in query:
            if qs.is_active():
                return qs.test_id, qs.sheet_number


class Sheet(models.Model):
    test_id = models.ForeignKey(Test)
    student_id = models.ForeignKey(Student)
    sheet_number = models.SmallIntegerField()
    points = models.SmallIntegerField(null=True)

    def __unicode__(self):
        return "{}, {}".format(self.student_id.index_number, self.test_id.name)

    def is_active(self):
        return self.test_id.end_time > timezone.now() > self.test_id.start_time

    objects = SheetManager()

    class Meta:
        verbose_name = "Arkusz"
        verbose_name_plural = "Arkusze"


class Results(models.Model):
    sheet_id  = models.ForeignKey(Sheet)
    question_id = models.ForeignKey(Question)
    a = models.BooleanField()
    b = models.BooleanField()
    c = models.BooleanField()
    d = models.BooleanField()
    e = models.BooleanField()
    f = models.BooleanField()


class SheetQuestions(models.Model):
    question_id = models.ForeignKey(Question)
    sheet_id = models.ForeignKey(Sheet)
    order_number = models.IntegerField()
    answer_order = models.CharField(max_length=6)
