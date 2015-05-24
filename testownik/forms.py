# -*- coding: utf-8 -*-
from django import forms
from models import UserProfile, Room
from django.contrib.auth.models import User
from django.forms.formsets import BaseFormSet
from django.contrib.admin.widgets import AdminDateWidget

from models import SheetQuestions, Question

class LoginForm(forms.Form):
    '''
    Forma wykozrystywana do logowania uzytkownika (prowadzacego).
    '''
    username = forms.CharField(
        label='Login',
        max_length=30,
        widget=forms.TextInput({'class': "form-control"}),
    )
    password = forms.CharField(
        label='Hasło:',
        widget=forms.PasswordInput({'class': "form-control"}),
    )


class StudentForm(forms.Form):
    '''
    Forma do wprowadzenia nr indeksu studenta.
    '''
    index = forms.IntegerField(
        label='Numer indeksu',
        widget=forms.NumberInput({'class': "form-control"}),
        )


class UploadFileForm(forms.Form):
    '''
    Forma do wyboru pliku.
    '''

    start = forms.CharField(label='Data początku',widget=forms.TextInput(attrs={'id': 'start', 'class': "form-control"}))
    end = forms.CharField(label='Data końca',widget=forms.TextInput(attrs={'id': 'end', 'class': "form-control"}))
    time = forms.CharField(label='Czas testu (min)', widget=forms.TextInput(attrs={'class': "form-control"}))
    file = forms.FileField(label='Plik', widget=forms.FileInput(attrs={'class': "form-control"}))
    room = forms.ChoiceField(label='Sala', choices=[(r.id, r.name) for r in Room.objects.all()], required=False)


class UserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    CHOICES = (('teacher', 'Prowadzacy',), ('supervisor', 'Pracownik administracji',))

    username = forms.CharField(
        label='Login',
        required=True,
        widget=forms.TextInput({'class': "form-control"}),
        )
    first_name = forms.CharField(
        label='Imię',
        required=True,
        widget=forms.TextInput({'class': "form-control"})
        )
    last_name = forms.CharField(
        label='Nazwisko',
        required=True,
        widget=forms.TextInput({'class': "form-control"})
        )
    password1 = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput({'class': "form-control"})
        )
    password2 = forms.CharField(
        label="Powtorz hasło",
        widget=forms.PasswordInput({'class': "form-control"})
        )
    choice_field = forms.ChoiceField(
        label=u"Typ użytkownika",
        widget=forms.RadioSelect(),
        choices=CHOICES,
        required=True,
        )

    def save(self):
        user = User(
            username = self.cleaned_data.get("username"),
            first_name = self.cleaned_data.get("first_name"),
            last_name = self.cleaned_data.get("last_name"),
        )
        user.set_password(self.cleaned_data.get("password1"))
        user.save()
        user_profile = UserProfile(
            user = user,
            is_teacher = self.cleaned_data.get("choice_field") == 'teacher',
            is_supervisor = self.cleaned_data.get("choice_field") == 'supervisor'
        )
        user_profile.save()
        return user


class AnswersForm(forms.Form):
    CHOICES = (('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F'))
    def __init__(self, *args,**kwargs):
        super(AnswersForm, self).__init__(*args,**kwargs)
        self.fields['choice_field'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=self.CHOICES, required=True, label='Pytanie')


class AnswersFormSet(BaseFormSet):
    def __init__(self, sheet_id, *args, **kwargs):
        self.sheet_id = sheet_id

        super(AnswersFormSet, self).__init__(*args, **kwargs)
        CHOICES = (('a', 'A',), ('b', 'B',), ('c', 'C',), ('d', 'D',), ('e', 'E',), ('f', 'F',))
        if self.sheet_id:
            query = SheetQuestions.objects.filter(sheet_id=sheet_id)
            for sq in query:
                self[sq.order_number-1].fields['choice_field'].label += " {}".format(sq.order_number)
                self[sq.order_number-1].fields['choice_field'].choices = CHOICES[:len(sq.answer_order)]

class EditTestForm(forms.Form):
    '''
    Forma do wyboru pliku.
    '''
    start = forms.CharField(label='Data początku',widget=forms.TextInput(attrs={'id': 'start', 'class': "form-control"}))
    end = forms.CharField(label='Data końca',widget=forms.TextInput(attrs={'id': 'end', 'class': "form-control"}))
    time = forms.CharField(label='Czas testu (min)', widget=forms.TextInput(attrs={'class': "form-control"}))