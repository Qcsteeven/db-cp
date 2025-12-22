from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Discipline, GradeSheet, Student


@receiver(post_save, sender=Student)
def create_grade_sheets_for_new_student(sender, instance, created, **kwargs):
    if created:
        disciplines = Discipline.objects.filter(specialty=instance.group.specialty)

        for discipline in disciplines:
            GradeSheet.objects.get_or_create(
                student=instance,
                discipline=discipline,
                semester=discipline.semester,
                defaults={
                    "grade": 0,
                    "date": date.today(),
                },
            )
