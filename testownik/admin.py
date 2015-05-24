from django.contrib import admin

from .models import Question, Student, Sheet, Test, UserProfile, SheetQuestions, Room, IP

#admin.site.register(Question)
admin.site.register(Student)
admin.site.register(Sheet)
admin.site.register(Test)
admin.site.register(UserProfile)
admin.site.register(Room)
admin.site.register(IP)
#admin.site.register(SheetQuestions)
