from TestSystem.settings import MEDIA_DIR

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.views.generic import View, DetailView, ListView

from models import Student, Sheet, SheetQuestions

from forms import UserCreationForm
from forms import LoginForm, StudentForm, UploadFileForm, AnswersForm, AnswersFormSet
from django.forms.formsets import formset_factory

import os
from functools import partial, wraps


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
                    redirect_to = request.POST.get('next', '')
                    return HttpResponseRedirect(redirect_to)
        return HttpResponse('nie udalo sie zalogowac')

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})


class PdfGeneratorView(View):
    '''
    Widok do wyswietlania pliku pdf.
    '''
    def get(self, request, *args):
        fileh = 'zestaw8.pdf'
        filename = os.path.join(MEDIA_DIR, 'test_id', str(fileh))
        with open(filename, 'r') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=some_file.pdf'
            return response


class SheetView(View):
    '''
    Widok do wysietlania gotowego arkusza.
    '''
    template_name = 'testownik/sheet.html'
    AnswerForm = formset_factory(wraps(AnswersForm)(partial(AnswersForm, 3)), extra=3, formset=AnswersFormSet)
    
    def get(self, request, *args):
        formset = self.AnswerForm()
        return render(request, self.template_name, {'nr_index': args[0], 'id': args[1], 'formset': formset})

    def post(self, request, *args):
        formset = self.AnswerForm(request.POST, request.FILES)
        if formset.is_valid():
            print formset.cleaned_data
            return HttpResponse('Poprawnie wypelniona forma')
        print formset.errors
        return HttpResponse('Blednie wypelniona forma')


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


class UserCreationView(View):
    '''
    Formularz do logowania
    '''
    template_name = 'testownik/create_user.html'
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print user.username
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
                )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/")
        return HttpResponse('nie udalo sie zarejestrowac')

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})


