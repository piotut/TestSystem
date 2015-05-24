from django.contrib import admin

from .models import Question, Student, Sheet, Test, UserProfile, SheetQuestions, Room, IP


class IPsInline(admin.StackedInline):
    model = IP
    extra = 3

class RoomAdmin(admin.ModelAdmin):
    inlines = [IPsInline]

admin.site.register(Student)
admin.site.register(Sheet)
admin.site.register(Test)
admin.site.register(UserProfile)
admin.site.register(Room, RoomAdmin)
