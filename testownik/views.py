from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.views.generic import View, DetailView, ListView

from testownik.models import Student, Sheet, SheetQuestions

from forms import LoginForm, StudentForm


class IndexView(View):
    '''
    Strona glowna
    '''
    template_name = 'testownik/index.html'

    def post(self, request):
        form = StudentForm(request.POST)

        if form.is_valid():
            index = form.cleaned_data['index']
            return HttpResponseRedirect(reverse('choose_test', args=[index]))

    def get(self, request):
        form = StudentForm()
        return render(request, self.template_name, {'form': form})


class ChooseTestView(ListView):
    '''
    Strona z wyborem testu sposrod dostepnych dla uzytkownika.
    '''
    template_name = 'testownik/choose_test.html'
    context_object_name = 'sheet_list'

    def get_queryset(self):
        return Sheet.objects.filter(student_id__index_number=self.args[0])


class LoginView(View):
    '''
    Formularz do logowania
    '''
    template_name = 'testownik/login.html'
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
                )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('brawo')
        return HttpResponse('nie udalo sie zalogowac')

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})


class SheetView(View):
    '''
    Formularz do wysietlania gotowego arkusza.
    '''
    def get(self, request, *args):
        return HttpResponse('Arkusz dla: '+args[0]+' o ID: '+args[1])