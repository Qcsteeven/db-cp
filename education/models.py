from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    surname = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    ROLE_CHOICES = [
        (1, "Сотрудник учебного отдела"),
        (2, "Сотрудник дирекции"),
        (3, "Преподаватель"),
    ]
    role = models.IntegerField(choices=ROLE_CHOICES, default=1, verbose_name="Роль")

    def __str__(self):
        return f"{self.surname} {self.first_name} {self.patronymic}".strip()


class Specialty(models.Model):
    code = models.CharField("Код", max_length=20)
    name = models.CharField("Наименование", max_length=255)

    def __str__(self):
        return f"{self.code} {self.name}"


class Group(models.Model):
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    name = models.CharField("Наименование", max_length=50)
    admission_year = models.IntegerField("Год поступления")

    def __str__(self):
        return self.name


class Student(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    surname = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)

    def __str__(self):
        return f"{self.surname} {self.first_name}"


class Discipline(models.Model):
    name = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=50, default="Экзамен")
    hours = models.PositiveIntegerField(default=72, verbose_name="Часы")
    specialty = models.ForeignKey(
        "Specialty", on_delete=models.CASCADE, null=True, blank=True
    )
    semester = models.ForeignKey(
        "Semester", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Semester(models.Model):
    number = models.IntegerField("Номер семестра")

    def __str__(self):
        return f"Семестр {self.number}"


class Curriculum(models.Model):
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    assessment_type = models.CharField("Вид аттестации", max_length=100)


class Teacher(models.Model):
    surname = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    position = models.CharField("Должность", max_length=100)

    def __str__(self):
        return f"{self.surname} {self.position}"


class GradeSheet(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        "Teacher", on_delete=models.CASCADE, null=True, blank=True
    )
    grade = models.IntegerField("Оценка")
    date = models.DateField("Дата")
