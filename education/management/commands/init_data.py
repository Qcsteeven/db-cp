import random
from datetime import date

from django.core.management.base import BaseCommand
from django.db.models.signals import post_save

from education.models import (
    Discipline,
    GradeSheet,
    Group,
    Semester,
    Specialty,
    Student,
    Teacher,
)
from education.signals import create_grade_sheets_for_new_student


class Command(BaseCommand):
    help = "Заполнение БД"

    def handle(self, *args, **options):
        post_save.disconnect(create_grade_sheets_for_new_student, sender=Student)
        self.stdout.write("Начало инициализации данных")

        try:
            semesters = {
                i: Semester.objects.get_or_create(number=i)[0] for i in range(1, 9)
            }

            is_it, _ = Specialty.objects.get_or_create(
                code="09.03.01",
                defaults={"name": "Информатика и вычислительная техника"},
            )
            is_is, _ = Specialty.objects.get_or_create(
                code="09.03.02",
                defaults={"name": "Информационные системы и технологии"},
            )

            teacher_main, _ = Teacher.objects.get_or_create(
                surname="Петров",
                first_name="Иван",
                defaults={"patronymic": "Сергеевич"},
            )
            teacher_sec, _ = Teacher.objects.get_or_create(
                surname="Сидоров",
                first_name="Алексей",
                defaults={"patronymic": "Николаевич"},
            )

            disciplines_config = [
                {
                    "name": "Математика",
                    "type": "Экзамен",
                    "hours": 144,
                    "sem": 1,
                    "specs": [is_it, is_is],
                },
                {
                    "name": "Программирование Python",
                    "type": "Зачет",
                    "hours": 72,
                    "sem": 3,
                    "specs": [is_it, is_is],
                },
                {
                    "name": "Базы данных",
                    "type": "Экзамен",
                    "hours": 108,
                    "sem": 5,
                    "specs": [is_it],
                },
                {
                    "name": "Базы данных",
                    "type": "Курсовая работа",
                    "hours": 36,
                    "sem": 5,
                    "specs": [is_it],
                },
                {
                    "name": "Web-программирование",
                    "type": "Экзамен",
                    "hours": 180,
                    "sem": 2,
                    "specs": [is_is],
                },
                {
                    "name": "Правоведение",
                    "type": "Зачет",
                    "hours": 36,
                    "sem": 5,
                    "specs": [is_it],
                },
            ]

            for d_info in disciplines_config:
                for spec in d_info["specs"]:
                    Discipline.objects.get_or_create(
                        name=d_info["name"],
                        specialty=spec,
                        semester=semesters[d_info["sem"]],
                        exam_type=d_info["type"],
                        defaults={"hours": d_info["hours"]},
                    )

            groups_to_create = [
                {"name": "ИСИб-23-1", "spec": is_it, "year": 2023},
                {"name": "ИСТб-23-1", "spec": is_is, "year": 2023},
                {"name": "ИСИб-25-1", "spec": is_it, "year": 2025},
            ]

            created_groups = []
            for g in groups_to_create:
                group, _ = Group.objects.get_or_create(
                    name=g["name"],
                    specialty=g["spec"],
                    defaults={"admission_year": g["year"]},
                )
                created_groups.append(group)

            surnames = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Попов", "Васильев"]
            names = ["Александр", "Дмитрий", "Максим", "Сергей"]
            patronymics = ["Иванович", "Петрович", "Сергеевич"]

            student_count = 0
            grade_count = 0

            for group in created_groups:
                group_disciplines = Discipline.objects.filter(specialty=group.specialty)

                for i in range(7):
                    student, created = Student.objects.get_or_create(
                        surname=random.choice(surnames),
                        first_name=random.choice(names),
                        patronymic=random.choice(patronymics),
                        group=group,
                    )
                    if created:
                        student_count += 1

                    for disc in group_disciplines:
                        current_t = (
                            teacher_main if "Математика" in disc.name else teacher_sec
                        )

                        _, g_created = GradeSheet.objects.get_or_create(
                            student=student,
                            discipline=disc,
                            semester=disc.semester,
                            defaults={
                                "teacher": current_t,
                                "grade": random.choice([3, 4, 5]),
                                "date": date.today(),
                            },
                        )
                        if g_created:
                            grade_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Создано студентов: {student_count}, записей в ведомостях: {grade_count}"
                )
            )

        finally:
            post_save.connect(create_grade_sheets_for_new_student, sender=Student)
            self.stdout.write("Сигналы восстановлены")
