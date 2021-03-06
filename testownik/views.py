#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TestSystem.settings import MEDIA_DIR

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone

from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import DeleteView

from django.contrib.auth.models import User
from models import Student, Sheet, SheetQuestions, Test, UserProfile, Room, IP

from forms import UserCreationForm, EditTestForm
from forms import LoginForm, StudentForm, UploadFileForm, AnswersForm, AnswersFormSet
from django.forms.formsets import formset_factory

from datetime import datetime
import os
import fnmatch

from SaveDBF import SaveDBF
from TestResults import TestResults, TestAnswers
from commons import convert_time

import csv

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
            return render(request, 'testownik/error.html', {'error_text': 'Dla studenta o numerze indeksu ' + str(index) + " nie ma aktywnego testu!"})
        return render(request, 'testownik/error.html', {'error_text': 'Niepoprawny numer indeksu!'})


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
        return render(request, 'testownik/error.html', {'error_text': 'Wystąpił błąd podczas próby logowania!'})

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

        ips = IP.objects.filter(room=sheet.test_id.room)
        if request.META.get('REMOTE_ADDR') in [x.ip for x in ips] or request.user.is_authenticated() or not ips:
            if sheet.start_time==None:
                sheet.start_time=datetime.now()
                sheet.save()
            return render(request, self.template_name, {'msg_points': sheet.points, 'student': sheet.student_id, 
            'id': sheet_id, 'formset': formset, 'sheet': sheet, 'answers': list_answers })
        else:
            return render(request, 'testownik/error.html', {'error_text': 'Adres IP, z którego próbujesz się połączyć jest błędny!'})

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
        return render(request, 'testownik/error.html', {'error_text': 'Błędnie wypełniona forma!'})


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

        s = SaveDBF(MEDIA_DIR, testId)
        
        new_test = Test.objects.get(id=testId)
        students = s.get_students_list()
        
        for index in students:
            try:
                 student = Student.objects.get(index_number=index)
            except Student.DoesNotExist:
                 continue
            else:
                sheets = student.sheet_set.all()
                for a_sheet in sheets:
                    if new_test.start_time > a_sheet.test_id.end_time:
                        pass
                    elif new_test.end_time < a_sheet.test_id.start_time:
                        pass
                    else:
                        print 'BLAD!!!'
                        print "Test start: %s" % new_test.start_time
                        print "Test end: %s" % new_test.end_time
                        print "Student start %s: " % a_sheet.test_id.start_time
                        print "Student end %s: " % a_sheet.test_id.end_time
                        raise ValueError
        s.save_test()

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
            try:
                test.room = Room.objects.get(id=form.cleaned_data.get('room'))
            except:
                test.room = None
            finally:
                test.save()
            try:
                self.handle_uploaded_file(test.id, request.FILES['file'])
            except:
                test.delete()
                msg = {'error': 'Wystąpił konflikt terminów. Test nie został dodany.'}
                return render(request, self.template_name, {'form': form, 'msg': msg})

            else:
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
        return render(request, 'testownik/error.html', {'error_text': 'Nie udało się zarejestrować!'})

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
                print '1'
                t = Test.objects.get(id=request.POST['test_id'])
                print t
                print form.cleaned_data
                t.start_time = convert_time(form.cleaned_data.get('start') or t.start_time)
                print t.end_time
                t.end_time = convert_time(form.cleaned_data.get('end') or t.end_time)
                t.time = form.cleaned_data.get('time') or t.time
                t.save()
            except:
                pass
            else:
                msg = {'correct': u"Zmieniono test: {}".format(t.name)}
            try:
                t = Test.objects.get(id=request.POST['test_id'])
                t.room = Room.objects.get(id=form.cleaned_data['room'])
            except:
                t.room = None
            else:
                msg = {'correct': u"Zmieniono test: {}".format(t.name)}
            finally:
                t.save()

            
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
        
        ips = IP.objects.filter(room=sheet.test_id.room)
        if request.META.get('REMOTE_ADDR') in [x.ip for x in ips] or request.user.is_authenticated() or not ips:
            return render(request, self.template_name, {'sheet': sheet})
        else:
            return render(request, 'testownik/error.html', {'error_text': 'Adres IP, z którego próbujesz się połączyć jest błędny!'})

class DeleteTestView(View):
    
    template_name = 'testownik/tests.html'

    def get(self, request, *args):
        print args
        t = Test.objects.get(id=self.args[0])
        t.delete()
        return HttpResponseRedirect(reverse('tests'))

class CSVSheetView(View):
    def get(self, *args):
        # Create the HttpResponse object with the appropriate CSV header.
        sheets = Sheet.objects.filter(test_id__id=self.args[0])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % sheets[0].test_id.name

        writer = csv.writer(response)
        writer.writerow(['nr_indeksu', 'imie_i_nazwisko', 'punkty'])

        for s in sheets:
            index = s.student_id.index_number
            name = "%s %s" % (s.student_id.first_name, s.student_id.last_name)
            points = s.points
            writer.writerow([index, name.encode("utf-8"), points])

        return response
