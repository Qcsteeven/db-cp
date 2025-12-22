from collections import defaultdict
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AssignTeacherForm, StudentForm
from .models import Discipline, GradeSheet, Group, Semester, Specialty, Student, Teacher


def is_registrar(user):
    return user.is_authenticated and int(user.role) == 1


def is_directorate(user):
    return user.is_authenticated and int(user.role) == 2


def is_teacher(user):
    return user.is_authenticated and int(user.role) == 3


@login_required
def main_window(request):
    return render(request, "main.html")


@login_required
def specialties_list(request):
    if not is_registrar(request.user):
        raise PermissionDenied
    if request.method == "POST":
        if "add_specialty" in request.POST:
            code = request.POST.get("code")
            name = request.POST.get("name")
            Specialty.objects.create(code=code, name=name)
            messages.success(request, f"Специальность '{name}' добавлена.")
        elif "edit_specialty" in request.POST:
            spec = get_object_or_404(Specialty, id=request.POST.get("specialty_id"))
            old_name = spec.name
            spec.code = request.POST.get("code")
            spec.name = request.POST.get("name")
            spec.save()
            messages.info(request, f"Специальность '{old_name}' изменена.")
        elif "delete_specialty" in request.POST:
            spec = get_object_or_404(Specialty, id=request.POST.get("specialty_id"))
            name = spec.name
            spec.delete()
            messages.warning(request, f"Специальность '{name}' удалена.")
        return redirect("specialties_list")
    specialties = Specialty.objects.all().order_by("code")
    return render(request, "specialties_list.html", {"specialties": specialties})


@login_required
def disciplines_list(request):
    if not is_registrar(request.user):
        raise PermissionDenied

    specialty_id = request.GET.get("specialty")
    specialty = get_object_or_404(Specialty, id=specialty_id) if specialty_id else None
    semesters = Semester.objects.all().order_by("number")

    if request.method == "POST":
        raw_hours = request.POST.get("hours")
        try:
            hours_val = int(raw_hours) if raw_hours else 0
        except ValueError:
            hours_val = -1

        if "add_discipline" in request.POST:
            name = request.POST.get("name")
            if hours_val <= 0:
                messages.error(
                    request, "Ошибка: Количество часов должно быть больше нуля."
                )
            else:
                Discipline.objects.create(
                    name=name,
                    exam_type=request.POST.get("exam_type"),
                    hours=hours_val,
                    specialty=specialty,
                    semester_id=request.POST.get("semester_id"),
                )
                messages.success(request, f"Дисциплина '{name}' добавлена.")

        elif "edit_discipline" in request.POST:
            disc = get_object_or_404(Discipline, id=request.POST.get("discipline_id"))

            # ВАЛИДАЦИЯ: Проверка при редактировании
            if hours_val <= 0:
                messages.error(
                    request,
                    f"Ошибка обновления: для дисциплины '{disc.name}' указано некорректное время.",
                )
            else:
                disc.name = request.POST.get("name")
                disc.exam_type = request.POST.get("exam_type")
                disc.hours = hours_val
                disc.semester_id = request.POST.get("semester_id")
                disc.save()
                messages.info(request, f"Дисциплина '{disc.name}' обновлена.")

        elif "delete_discipline" in request.POST:
            disc = get_object_or_404(Discipline, id=request.POST.get("discipline_id"))
            name = disc.name
            disc.delete()
            messages.warning(request, f"Дисциплина '{name}' удалена.")

        return redirect(
            f"{request.path}?specialty={specialty_id}" if specialty_id else request.path
        )

    if specialty:
        disciplines = Discipline.objects.filter(specialty=specialty).select_related(
            "semester"
        )
        title = f"Дисциплины: {specialty.name}"
    else:
        disciplines = Discipline.objects.all().select_related("semester")
        title = "Все дисциплины"

    return render(
        request,
        "disciplines_list.html",
        {
            "disciplines": disciplines,
            "title": title,
            "specialty": specialty,
            "semesters": semesters,
        },
    )


@login_required
def assign_teacher_view(request, discipline_id, group_id):
    if request.user.role not in [1, 2]:
        messages.error(request, "У вас нет прав для назначения преподавателей.")
        return redirect("main")
    discipline = get_object_or_404(Discipline, id=discipline_id)
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST":
        form = AssignTeacherForm(request.POST)
        if form.is_valid():
            teacher = form.cleaned_data["teacher"]
            updated_count = GradeSheet.objects.filter(
                discipline=discipline, student__group=group
            ).update(teacher=teacher)
            if updated_count == 0:
                students = Student.objects.filter(group=group)
                for student in students:
                    GradeSheet.objects.update_or_create(
                        student=student,
                        discipline=discipline,
                        semester=discipline.semester,
                        defaults={"teacher": teacher},
                    )
                updated_count = students.count()
            messages.success(
                request,
                f"Преподаватель {teacher.surname} назначен. Обновлено записей: {updated_count}.",
            )
            return redirect(
                "group_selection_for_discipline", discipline_id=discipline.id
            )
    else:
        current_entry = GradeSheet.objects.filter(
            discipline=discipline, student__group=group
        ).first()
        initial_data = (
            {"teacher": current_entry.teacher}
            if current_entry and current_entry.teacher
            else {}
        )
        form = AssignTeacherForm(initial=initial_data)
    return render(
        request,
        "assign_teacher.html",
        {"form": form, "discipline": discipline, "group": group},
    )


@login_required
def group_students_list_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students = Student.objects.filter(group=group).order_by("surname")
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.group = group
            student.save()
            messages.success(request, f"Студент {student.surname} добавлен.")
            return redirect("group_students_list", group_id=group.id)
    else:
        form = StudentForm()
    return render(
        request,
        "group_students_list.html",
        {"group": group, "students": students, "form": form},
    )


@login_required
def delete_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    group_id = student.group.id
    name = f"{student.surname} {student.first_name}"
    student.delete()
    messages.warning(request, f"Студент {name} удален.")
    return redirect("group_students_list", group_id=group_id)


@login_required
def grade_entry_view(request, discipline_id, group_id):
    discipline = get_object_or_404(Discipline, id=discipline_id)
    group = get_object_or_404(Group, id=group_id)
    students = Student.objects.filter(group=group)
    if request.user.role != 2:
        for student in students:
            GradeSheet.objects.get_or_create(
                student=student,
                discipline=discipline,
                semester=discipline.semester,
                defaults={"grade": 0},
            )
    grades = GradeSheet.objects.filter(
        discipline=discipline, student__group=group
    ).select_related("student")
    if request.method == "POST":
        if request.user.role == 2:
            messages.error(request, "У Дирекции нет прав на изменение оценок.")
            return redirect(
                "grade_entry", discipline_id=discipline.id, group_id=group.id
            )
        for grade_obj in grades:
            new_grade = request.POST.get(f"grade_{grade_obj.id}")
            if new_grade is not None:
                grade_obj.grade = new_grade
                grade_obj.save()
        messages.success(request, "Оценки сохранены.")
        return redirect("grade_entry", discipline_id=discipline.id, group_id=group.id)
    return render(
        request,
        "grade_entry.html",
        {"discipline": discipline, "group": group, "grades": grades},
    )


@login_required
def control_forms_view(request):
    semester_num = request.GET.get("semester", 1)
    disciplines = Discipline.objects.filter(
        semester__number=semester_num
    ).select_related("specialty")
    grouped_data = defaultdict(lambda: {"exams": [], "tests": [], "course_works": []})
    for d in disciplines:
        spec_name = f"{d.specialty.code} {d.specialty.name}"
        if "Экзамен" in d.exam_type:
            grouped_data[spec_name]["exams"].append(d.name)
        elif "зачёт" in d.exam_type.lower():
            grouped_data[spec_name]["tests"].append(d.name)
        elif "Курсовая" in d.exam_type:
            grouped_data[spec_name]["course_works"].append(d.name)
    return render(
        request,
        "control_forms_doc.html",
        {
            "semester": semester_num,
            "grouped_data": dict(grouped_data.items()),
        },
    )


@login_required
def student_report_view(request, student_id):
    student = get_object_or_404(
        Student.objects.select_related("group__specialty"), id=student_id
    )
    try:
        course_num = int(request.GET.get("course", 1))
    except (ValueError, TypeError):
        course_num = 1
    sem_end = course_num * 2
    sem_start = sem_end - 1
    grades_queryset = (
        GradeSheet.objects.filter(
            student=student, semester__number__in=[sem_start, sem_end]
        )
        .select_related("discipline", "semester")
        .order_by("semester__number", "discipline__name")
    )
    average_grade = grades_queryset.aggregate(Avg("grade"))["grade__avg"]
    return render(
        request,
        "student_report.html",
        {
            "student": student,
            "course": course_num,
            "grades": grades_queryset,
            "average_grade": average_grade,
            "sem_start": sem_start,
            "sem_end": sem_end,
            "today": date.today(),
        },
    )


@login_required
def students_search_view(request):
    query = request.GET.get("q", "")
    if query:
        students = Student.objects.filter(surname__icontains=query).select_related(
            "group__specialty"
        )
    else:
        students = (
            Student.objects.all().select_related("group__specialty").order_by("surname")
        )
    return render(
        request, "students_search.html", {"students": students, "query": query}
    )


@login_required
def discipline_selection_view(request):
    if request.user.role == 3:
        teacher_inst = Teacher.objects.filter(surname=request.user.surname).first()
        if teacher_inst:
            discipline_ids = (
                GradeSheet.objects.filter(teacher=teacher_inst)
                .values_list("discipline_id", flat=True)
                .distinct()
            )
            disciplines = Discipline.objects.filter(id__in=discipline_ids)
        else:
            disciplines = Discipline.objects.none()
    else:
        disciplines = Discipline.objects.all()
    return render(request, "discipline_selection.html", {"disciplines": disciplines})


@login_required
def group_selection_view(request, discipline_id):
    discipline = get_object_or_404(Discipline, id=discipline_id)
    groups = Group.objects.filter(specialty=discipline.specialty)
    return render(
        request, "group_selection.html", {"discipline": discipline, "groups": groups}
    )


@login_required
def group_selection(request):
    groups = Group.objects.all()
    return render(request, "main.html", {"groups": groups})


@login_required
def groups_list(request):
    if int(request.user.role) != 2:
        raise PermissionDenied(
            "Доступ к управлению составом групп есть только у сотрудника дирекции."
        )
    groups = Group.objects.all().select_related("specialty")
    return render(request, "groups_list.html", {"groups": groups})


@login_required
def grading_window(request, group_id):
    if not (is_registrar(request.user) or is_teacher(request.user)):
        raise PermissionDenied
    group = get_object_or_404(Group, id=group_id)
    students = Student.objects.filter(group=group)
    return render(request, "main.html", {"group": group, "students": students})


@login_required
def student_card(request, student_id):
    if not (is_registrar(request.user) or is_directorate(request.user)):
        raise PermissionDenied
    student = get_object_or_404(Student, id=student_id)
    return render(request, "main.html", {"student": student})


@login_required
def study_plan(request):
    if not is_registrar(request.user):
        raise PermissionDenied
    return render(request, "main.html")


@login_required
def curriculum_doc_view(request):
    specialties = Specialty.objects.prefetch_related("discipline_set").all()
    return render(
        request,
        "curriculum_doc.html",
        {"specialties": specialties, "title": "Учебный план ИРНИТУ"},
    )


@login_required
def course_selection_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = [1, 2, 3, 4]
    return render(
        request, "course_selection.html", {"student": student, "courses": courses}
    )
