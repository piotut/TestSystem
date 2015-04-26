from TestSystem.settings import MEDIA_DIR

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from django.views.generic import View, DetailView, ListView

from models import Student, Sheet, SheetQuestions, Test, UserProfile

from forms import UserCreationForm
from forms import LoginForm, StudentForm, UploadFileForm, AnswersForm, AnswersFormSet
from django.forms.formsets import formset_factory

from datetime import datetime
from re import match
import os
import fnmatch

from SaveDBF import save_students, save_sheets

class IndexView(View):
    '''
    Strona glowna
    '''
    template_name = 'testownik/index.html'

    def post(self, request):
        form = StudentForm(request.POST)

        if form.is_valid():
            index = form.cleaned_data['index']
            return HttpResponseRedirect(reverse('sheet', args=[index]))

    def get(self, request):
        form = StudentForm()
        return render(request, self.template_name, {'form': form})


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
                    return HttpResponseRedirect(reverse('upload'))
        return HttpResponse('Nie udalo sie zalogowac')

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})


class PdfGeneratorView(View):
    '''
    Widok do wyswietlania pliku pdf.
    '''
    def get(self, request, *args):
        test, sheet_number = Sheet.objects.get_test_and_sheet_number(13538)
        fileh = 'testy_pdf/zestaw{}.pdf'.format(sheet_number)
        filename = os.path.join(MEDIA_DIR, str(test.id), str(fileh))

        with open(filename, 'r') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=some_file.pdf'
            return response


class SheetView(View):
    '''
    Widok do wysietlania gotowego arkusza. Arkusz musi byc aktywny.
    '''
    template_name = 'testownik/sheet.html'
    
    def get(self, request, *args):
        sheet_list = Sheet.objects.filter(student_id__index_number=self.args[0])
        sheet_id = 0
        for sheet in sheet_list:
            if sheet.is_active():
                sheet_id = sheet.id
                questions_no = len(SheetQuestions.objects.filter(sheet_id=sheet_id))
                AnswerForm = formset_factory(AnswersForm, extra=questions_no, formset=AnswersFormSet)
                formset = AnswerForm(sheet_id)
                return render(request, self.template_name, {'nr_index': args[0], 'id': sheet_id, 'formset': formset})
        return HttpResponse('Brak aktywnego testu')

    def post(self, request, *args):
        AnswerForm = formset_factory(AnswersForm, formset=AnswersFormSet)
        formset = AnswerForm(0, request.POST, request.FILES)
        if formset.is_valid():
            return HttpResponse('Poprawnie wypelniona forma')
        print formset.errors
        return HttpResponse('Blednie wypelniona forma')


class UploadFileView(View):
    '''
    Widok do importu plikow na serwer.
    url /upload
    '''
    template_name = 'testownik/upload.html'

    def handle_uploaded_file(self, testId, fileh):
        filename = os.path.join(MEDIA_DIR, str(testId), str(fileh))
        dir = os.path.dirname(filename)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(filename, 'wb+') as destination:
            for chunk in fileh.chunks():
                destination.write(chunk)
        os.system('unzip -o '+ filename +' -d '+dir+'/')
        os.system('rm ' + filename)

        for root, dirnames, filenames in os.walk(dir):
            for filename in fnmatch.filter(filenames, 'testy.dbf'):
                matchDir = root

        os.system('mv --force '+ matchDir +'/* ' +dir)

        testy_dbf = os.path.join(MEDIA_DIR, str(testId), "testy.dbf")
        save_students(testy_dbf)
        save_sheets(testy_dbf, testId)

    def convert_time(self, time):
        regex = '([0-9]){4}/([0-9]){2}/([0-9]){2} ([0-9]){2}:([0-9]){2}'
        m = match(regex, time).groups()
        return datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]), 0)

    def get(self, request):
        form = UploadFileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            print form.cleaned_data['start']
            test = Test(
                name=form.cleaned_data['name'],
                start_time = self.convert_time(form.cleaned_data['start']),
                end_time = self.convert_time(form.cleaned_data['end']),
                author_id = UserProfile.objects.get(user__id=request.user.id)
                )
            test.save()
            print 'test save przeszlo'
            self.handle_uploaded_file(test.id, request.FILES['file'])
            return HttpResponse('zaladowano plik')
        print form.errors
        return HttpResponse('wystapil blad')


class UserCreationView(View):
    '''
    Formularz do logowania
    '''
    template_name = 'testownik/create_user.html'
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
