from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_teacher = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)

    def __unicode__(self):
        return "{}".format(self.user.username)


class Student(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    index_number = models.IntegerField()

    def __unicode__(self):
        return "{} {}, {}".format(self.first_name, self.last_name, self.index_number)


class Question(models.Model):
    a_points = models.SmallIntegerField()
    b_points = models.SmallIntegerField()
    c_points = models.SmallIntegerField()
    d_points = models.SmallIntegerField()
    e_points = models.SmallIntegerField()
    f_points = models.SmallIntegerField()


class Test(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    author_id = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return "{} ({}-{}),{}".format(self.name, self.start_time, self.end_time, self.author_id)


class Sheet(models.Model):
    test_id = models.ForeignKey(Test)
    student_id = models.ForeignKey(Student)

    def is_active(self):
        return self.test_id.end_time > timezone.now() > self.test_id.start_time


class Results(models.Model):
    sheet_id  = models.ForeignKey(Sheet)
    question_id = models.OneToOneField(Question)
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
