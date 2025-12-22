from django import forms

from education.models import Student, Teacher

from .models import Discipline


class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ["name", "exam_type", "semester", "hours"]

    def clean_hours(self):
        hours = self.cleaned_data.get("hours")
        if hours is not None and hours <= 0:
            raise forms.ValidationError("Количество часов должно быть больше нуля.")
        return hours


class AssignTeacherForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        label="Выберите преподавателя",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["surname", "first_name", "patronymic"]
        labels = {
            "surname": "Фамилия",
            "first_name": "Имя",
            "patronymic": "Отчество",
        }
        widgets = {
            "surname": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "patronymic": forms.TextInput(attrs={"class": "form-control"}),
        }
