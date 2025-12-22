import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from education.models import Teacher


class Command(BaseCommand):
    help = "Автоматическое создание администратора и системных пользователей"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "registrar")
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=os.getenv("DJANGO_SUPERUSER_EMAIL", "reg@univ.ru"),
                password=os.getenv("DJANGO_SUPERUSER_PASSWORD", "password123"),
                surname="Учебного",
                first_name="Отдела",
                patronymic="Сотрудник",
                role=1,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Суперпользователь "{username}" создан.')
            )

        system_users = [
            {
                "username": "directorate",
                "password": "password123",
                "role": 2,
                "surname": "Сотрудник",
                "first_name": "Дирекции",
                "patronymic": "Института",
            },
            {
                "username": "teacher",
                "password": "password123",
                "role": 3,
                "surname": "Петров",
                "first_name": "Иван",
                "patronymic": "Сергеевич",
            },
        ]

        for u_data in system_users:
            user, created = User.objects.get_or_create(
                username=u_data["username"],
                defaults={
                    "role": u_data["role"],
                    "surname": u_data["surname"],
                    "first_name": u_data["first_name"],
                    "patronymic": u_data["patronymic"],
                    "is_staff": True,
                },
            )
            if created:
                user.set_password(u_data["password"])
                user.save()

                if u_data["role"] == 3:
                    Teacher.objects.get_or_create(
                        surname=u_data["surname"],
                        first_name=u_data["first_name"],
                        defaults={"patronymic": u_data["patronymic"]},
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Пользователь "{user.username}" (ФИО: {user.surname} {user.first_name}) создан.'
                    )
                )
