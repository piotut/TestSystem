from django import forms
from models import UserProfile
from django.contrib.auth.models import User
from django.forms.formsets import BaseFormSet

from models import SheetQuestions, Question

class LoginForm(forms.Form):
    '''
    Forma wykozrystywana do logowania uzytkownika (prowadzacego).
    '''
    username = forms.CharField(label='login', max_length=30)
    password = forms.CharField(label='haslo:', widget=forms.PasswordInput())


class StudentForm(forms.Form):
    '''
    Forma do wprowadzenia nr indeksu studenta.
    '''
    index = forms.IntegerField(label='nr_indeksu')


class UploadFileForm(forms.Form):
    '''
    Forma do wyboru pliku.
    '''
    title = forms.CharField(max_length=50)
    file = forms.FileField()

class UserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    CHOICES = (('teacher', 'Prowadzacy',), ('supervisor', 'Nadzorca',))

    username = forms.CharField(label='login', required=True)
    first_name = forms.CharField(label='imie', required=True)
    last_name = forms.CharField(label='nazwisko', required=True)
    password1 = forms.CharField(label="haslo", widget=forms.PasswordInput)
    password2 = forms.CharField(label="powtorz haslo", widget=forms.PasswordInput)
    choice_field = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES, required=True)

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
        print sheet_id

        super(AnswersFormSet, self).__init__(*args, **kwargs)
        CHOICES = (('a', 'A',), ('b', 'B',), ('c', 'C',), ('d', 'D',), ('e', 'E',), ('f', 'F',))
        if self.sheet_id:
            query = SheetQuestions.objects.filter(sheet_id=sheet_id)
            for sq in query:
                self[sq.order_number-1].fields['choice_field'].label += " {}".format(sq.order_number)
                self[sq.order_number-1].fields['choice_field'].choices = CHOICES[:len(sq.answer_order)]