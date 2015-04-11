from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from django.views.generic import View, DetailView

from testownik.models import Student, Sheet

from forms import LoginForm


class IndexView(View):
    '''
    Strona glowna
    '''
    template_name = 'testownik/index.html'

    def get(self, request):
        return render(request, self.template_name)


class ChooseTestView(DetailView):
    '''
    Strona z wyborem testu sposrod dostepnych dla uzytkownika
    '''
    template_name = 'testownik/choose_test.html'
    queryset = Sheet.objects.filter(student_id=1)
    context_object_name = 'sheet_list'

    def get(self, request):
        return render(request, self.template_name)

class LoginView(View):
    '''
    Formularz do logowania
    '''
    template_name = 'testownik/login.html'
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            print form.cleaned_data['username']
            print form.cleaned_data['password']
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
                )
            print user
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('brawo')
        return HttpResponse('nie udalo sie zalogowac')

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})