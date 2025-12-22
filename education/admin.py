from django.contrib import admin

from .models import Discipline, GradeSheet, Group, Semester, Specialty, Student


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "semester", "hours")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("surname", "first_name", "group")


admin.site.register(Semester)
admin.site.register(Group)
admin.site.register(GradeSheet)
