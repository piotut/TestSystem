from django.db import models
from django.contrib.auth.models import User

class Teacher(User):
    pass


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
    start_time = models.TimeField()
    end_time = models.TimeField()
    author_id = models.ForeignKey(Teacher)


class Sheet(models.Model):
    test_id = models.ForeignKey(Test)
    student_id = models.ForeignKey(Student)


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
