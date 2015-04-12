from django.contrib import admin

from .models import Question, Student, Sheet, Test, Teacher, SheetQuestions

admin.site.register(Question)
admin.site.register(Student)
admin.site.register(Sheet)
admin.site.register(Test)
admin.site.register(Teacher)
admin.site.register(SheetQuestions)
