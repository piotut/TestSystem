from TestSystem.settings import MEDIA_DIR

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from django.views.generic import View, DetailView, ListView

from django.contrib.auth.models import User
from models import Student, Sheet, SheetQuestions, Test, UserProfile

from forms import UserCreationForm
from forms import LoginForm, StudentForm, UploadFileForm, AnswersForm, AnswersFormSet
from django.forms.formsets import formset_factory

from datetime import datetime
from re import match
import os
import fnmatch

from SaveDBF import SaveDBF
from TestResults import TestResults

class IndexView(View):
    '''
    Strona glowna
    '''
    template_name = 'testownik/index.html'

    def post(self, request):
        form = StudentForm(request.POST)

        if form.is_valid():
            index = form.cleaned_data['index']
            sheet_list = Sheet.objects.filter(student_id__index_number=index)
            for sheet in sheet_list:
                if sheet.is_active():
                    if sheet.points != None:
                        return render(request, 'testownik/sheet.html', {'msg_points': sheet.points})
                    else:
                        return HttpResponseRedirect(reverse('sheet', args=[sheet.id]))
            return HttpResponse('Brak aktywnego testu dla studenta o indeksie {}'.format(index))


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
        test, sheet_number = Sheet.objects.get_test_and_sheet_number(self.args[0])
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
        sheet_id = self.args[0]
        sheet = Sheet.objects.get(id=sheet_id)
        questions_no = len(SheetQuestions.objects.filter(sheet_id=sheet_id))
        AnswerForm = formset_factory(AnswersForm, extra=questions_no, formset=AnswersFormSet)
        formset = AnswerForm(sheet_id)
        if sheet.points:
            return render(request, self.template_name, {'msg_points': sheet.points})
        return render(request, self.template_name, {'student': sheet.student_id, 'id': sheet_id, 'formset': formset})        

    def post(self, request, *args):
        AnswerForm = formset_factory(AnswersForm, formset=AnswersFormSet)
        formset = AnswerForm(0, request.POST, request.FILES)
        sheet = Sheet.objects.get(id=args[0])
        if formset.is_valid():
            if sheet.points != None:
                return render(request, self.template_name, {'msg_points': sheet.points})
            result = TestResults(formset.cleaned_data, args[0])
            return render(request, self.template_name, {'msg_points': result.points})
        #print formset.errors
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

        s = SaveDBF(MEDIA_DIR)
        s.save_test(testId)

    def convert_time(self, time):
        regex = '([0-9]{4})/([0-9]{2})/([0-9]{2}) ([0-9]{2}):([0-9]{2})'
        m = match(regex, time).groups()
        return datetime(int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4]), 0)

    def get(self, request):
        form = UploadFileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            test = Test(
                name=form.cleaned_data['name'],
                start_time = self.convert_time(form.cleaned_data['start']),
                end_time = self.convert_time(form.cleaned_data['end']),
                author_id = UserProfile.objects.get(user__id=request.user.id)
                )
            test.save()
            self.handle_uploaded_file(test.id, request.FILES['file'])
            return HttpResponse('zaladowano plik')
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


class TestListView(ListView):
    '''
    Lista testow prowadzacego wraz z informacjami o nich
    '''
    template_name = 'testownik/tests.html'

    def get_queryset(self, *args):
        return Test.objects.filter(author_id__user=self.request.user)

class SheetListView(ListView):
    '''
    Lista testow prowadzacego wraz z informacjami o nich
    '''
    template_name = 'testownik/sheets.html'

    def get_queryset(self, *args):
        return Sheet.objects.filter(test_id__id=self.args[0])
