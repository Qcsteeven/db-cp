from django.urls import path

from . import views

urlpatterns = [
    path("", views.main_window, name="main"),
    path("specialties/", views.specialties_list, name="specialties_list"),
    path("disciplines/", views.disciplines_list, name="disciplines_list"),
    path(
        "reports/student-card/<int:student_id>/",
        views.student_card,
        name="student_card",
    ),
    path("reports/study-plan/", views.study_plan, name="study_plan"),
    path("control-forms/", views.control_forms_view, name="control_forms"),
    path("curriculum-doc/", views.curriculum_doc_view, name="curriculum_doc"),
    path("directorate/students/", views.students_search_view, name="students_search"),
    path(
        "directorate/disciplines/",
        views.discipline_selection_view,
        name="discipline_selection",
    ),
    path(
        "directorate/disciplines/<int:discipline_id>/groups/",
        views.group_selection_view,
        name="group_selection_for_discipline",
    ),
    path(
        "grade-entry/<int:discipline_id>/<int:group_id>/",
        views.grade_entry_view,
        name="grade_entry",
    ),
    path(
        "directorate/students/<int:student_id>/course-selection/",
        views.course_selection_view,
        name="course_selection",
    ),
    path(
        "directorate/students/<int:student_id>/report/",
        views.student_report_view,
        name="student_report",
    ),
    path(
        "groups/<int:group_id>/students/",
        views.group_students_list_view,
        name="group_students_list",
    ),
    path(
        "students/<int:student_id>/delete/",
        views.delete_student_view,
        name="delete_student",
    ),
    path(
        "assign-teacher/<int:discipline_id>/<int:group_id>/",
        views.assign_teacher_view,
        name="assign_teacher",
    ),
    path("groups/select/", views.group_selection, name="group_selection"),
    path("groups/<int:group_id>/grades/", views.grading_window, name="grading_window"),
]
