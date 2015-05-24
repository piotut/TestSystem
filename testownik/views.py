#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TestSystem.settings import MEDIA_DIR

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from django.views.generic import View, DetailView, ListView

from django.contrib.auth.models import User
from models import Student, Sheet, SheetQuestions, Test, UserProfile

from forms import UserCreationForm, EditTestForm
from forms import LoginForm, StudentForm, UploadFileForm, AnswersForm, AnswersFormSet
from django.forms.formsets import formset_factory

from datetime import datetime
import os
import fnmatch

from SaveDBF import SaveDBF
from TestResults import TestResults, TestAnswers
from commons import convert_time

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
                        return HttpResponseRedirect(reverse('confirm', args=[sheet.id]))
            return HttpResponse('Brak aktywnego testu dla studenta o indeksie {}'.format(index))
        return HttpResponse('Niepoprawny format numeru indeksu');


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
        print 'test'
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
        
        answers = TestAnswers(sheet_id)
        list_answers = answers.get_answers()

        return render(request, self.template_name, {'msg_points': sheet.points, 'student': sheet.student_id, 
            'id': sheet_id, 'formset': formset, 'sheet': sheet, 'answers': list_answers })        

    def post(self, request, *args):
        AnswerForm = formset_factory(AnswersForm, formset=AnswersFormSet)
        formset = AnswerForm(0, request.POST, request.FILES)
        sheet = Sheet.objects.get(id=args[0])
        if formset.is_valid():
            if sheet.points == None:
                #return render(request, self.template_name, {'msg_points': sheet.points})
                result = TestResults(formset.cleaned_data, args[0])
            #return render(request, self.template_name, {'msg_points': result.points})
            return HttpResponseRedirect(reverse('sheet', args=[args[0]]))
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
        os.system('unzip -o "'+ filename +'" -d "'+dir+'"/')
        os.system('rm "' + filename + '"')

        for root, dirnames, filenames in os.walk(dir):
            for filename in fnmatch.filter(filenames, 'testy.dbf'):
                matchDir = root

        os.system('mv --force "'+ matchDir +'"/* "' +dir+'"')

        s = SaveDBF(MEDIA_DIR)
        s.save_test(testId)

    def get_test_name_from_file(self, test_id):
        description_filename = "opisTestu.txt"
        description_path = os.path.join(MEDIA_DIR, str(test_id), description_filename)
        print description_path
        
        with open(description_path, 'r') as description_file:
            lines = description_file.read().splitlines()
            test_name = lines[0].split('= ')[1]
            name_string = "%s (%s)" % (test_name, datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
            return name_string

    def get(self, request, *args, **kwargs):
        form = UploadFileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        msg = ''

        if form.is_valid():
            test = Test(
                start_time = convert_time(form.cleaned_data['start']),
                end_time = convert_time(form.cleaned_data['end']),
                author_id = UserProfile.objects.get(user__id=request.user.id),
                time = int(form.cleaned_data['time'])
                )
            test.save()
            self.handle_uploaded_file(test.id, request.FILES['file'])
            test.name = self.get_test_name_from_file(test.id)
            test.save()
            return HttpResponseRedirect(reverse('tests'))
        else:
            msg = {'error': u'Wystąpił błąd podczas ładowania pliku.'}
            form = UploadFileForm()
            return render(request, self.template_name, {'form': form, 'msg': msg})


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
                    return HttpResponseRedirect(reverse('tests'))
        return HttpResponse('nie udalo sie zarejestrowac')

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})


class TestListView(View):
    '''
    Lista testow prowadzacego wraz z informacjami o nich
    '''
    template_name = 'testownik/tests.html'
    my_form = EditTestForm

    def post(self, request):
        form = self.my_form(request.POST)

        msg = {'error': u"Wystąpił błąd przy próbie edytowania testu."}
        if form.is_valid():
            try:
                t = Test.objects.get(id=request.POST['test_id'])
                t.start_time = convert_time(form.cleaned_data['start'])
                t.end_time = convert_time(form.cleaned_data['end'])
                t.time = form.cleaned_data['time']
                t.save()
            except:
                pass
            else:
                msg = {'correct': u"Zmieniono test: {}".format(t.name)}
            
        tests_list = Test.objects.filter(author_id__user=request.user)

        return render(request, self.template_name, {'form': form, 'object_list': tests_list, 'msg':msg})

    def get(self, request):
        form = self.my_form()
        tests_list = Test.objects.filter(author_id__user=request.user)
        return render(request, self.template_name, {'form': form, 'object_list': tests_list})

class SheetListView(ListView):
    '''
    Lista testow prowadzacego wraz z informacjami o nich
    '''
    template_name = 'testownik/sheets.html'

    def get_queryset(self, *args):
        return Sheet.objects.filter(test_id__id=self.args[0])

class ConfirmTestStartView(View):
    '''
    Strona sluzaca do pobrania decyzji studenta czy chce przystapic do testu
    '''
    template_name = 'testownik/confirm.html'

    def get(self, request, *args):
        sheet = Sheet.objects.get(id=args[0])
        return render(request, self.template_name, {'sheet': sheet})

