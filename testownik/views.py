from TestSystem.settings import MEDIA_DIR

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.views.generic import View, DetailView, ListView

from testownik.models import Student, Sheet, SheetQuestions

from forms import LoginForm, StudentForm, UploadFileForm

import os


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


class UploadFileView(View):
    '''
    Widok do importu plikow na serwer.
    '''
    template_name = 'testownik/upload.html'

    def handle_uploaded_file(self, fileh):
        filename = os.path.join(MEDIA_DIR, 'test_id', str(fileh))
        dir = os.path.dirname(filename)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(filename, 'wb+') as destination:
            for chunk in fileh.chunks():
                destination.write(chunk)

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        print request.FILES
        if form.is_valid():
            self.handle_uploaded_file(request.FILES['file'])
            return HttpResponse('zaladowano plik')
        return HttpResponse('wystapil blad')

    def get(self, request):
        form = UploadFileForm()
        return render(request, self.template_name, {'form': form})
