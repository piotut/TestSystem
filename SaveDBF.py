#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbfpy import dbf

from testownik.models import Student, Test, Sheet, SheetQuestions, Question

import os

class SaveDBF():
    def __init__(self, MEDIA_DIR, test_id, testy_dbf_filename="testy.dbf", zestawy_dbf_filename="zestawy.dbf"):
        self.MEDIA_DIR = MEDIA_DIR
	self.test_id = test_id

        self.testy_dbf_filename = testy_dbf_filename
        self.zestawy_dbf_filename = zestawy_dbf_filename

        self.testy_dbf_path = os.path.join(self.MEDIA_DIR, str(test_id), self.testy_dbf_filename)
        self.zestawy_dbf_path = os.path.join(self.MEDIA_DIR, str(test_id), self.zestawy_dbf_filename)

        self.testy_dbf = None
        self.zestawy_dbf = None

        self.test = None

        self.saved_questions = set()

    def get_students_list(self):
        self.open_dbf_files()
        students = self.read_students()
        self.close_dbf_files()
        return students

    def read_students(self):
        s = []
        for record in self.testy_dbf:
            album = int(record['NR_ALBUMU'])
            if album != 0:
                s.append(album)
        return s

    def save_test(self):
        try:
            self.test = Test.objects.get(id=self.test_id)
        except (Test.DoesNotExist, Test.MultipleObjectsReturned):
            raise Exception("Test ERROR!")

        self.open_dbf_files()
        self.save_sheets()
        self.close_dbf_files()

    def open_dbf_files(self):
        self.testy_dbf = dbf.Dbf(self.testy_dbf_path)
        if not self.testy_dbf:
            raise Exception("Can't open %s file!" % self.testy_dbf_path)
        self.zestawy_dbf = dbf.Dbf(self.zestawy_dbf_path)
        if not self.zestawy_dbf:
            raise Exception("Can't open %s file!" % self.zestawy_dbf_path)

    def save_sheets(self):
        for rec_testy_dbf in self.testy_dbf:
            try:
                student = self.save_student(rec_testy_dbf)
            except ValueError:
                ## INDEX NR 0
                continue
            except Exception:
                student = Student.objects.get(index_number=int(rec_testy_dbf['NR_ALBUMU']))
                sheet = self.save_one_sheet(rec_testy_dbf, student)
                self.save_sheet_questions(sheet)
            else:
                sheet = self.save_one_sheet(rec_testy_dbf, student)
                self.save_sheet_questions(sheet)

    def save_student(self, rec_testy_dbf):
        index_number = int(rec_testy_dbf['NR_ALBUMU'])
        if index_number == 0:
            raise ValueError
        student_exists = Student.objects.filter(index_number=index_number).count()
        if student_exists:
            raise Exception("STUDENT ALREADY EXISTS!")
        else:
            first_name = rec_testy_dbf['IMIE'].decode('windows-1250')
            last_name = rec_testy_dbf['NAZWISKO'].decode('windows-1250')

            student = Student()
            student.first_name = first_name
            student.last_name = last_name
            student.index_number = index_number
            student.save()
        return student

    def save_one_sheet(self, rec_testy_dbf, student):
        number = int(rec_testy_dbf['NR_ZESTAWU'])

        sheet = Sheet()
        sheet.test_id = self.test
        sheet.student_id = student
        sheet.sheet_number = number
        sheet.save()

        return sheet

    def save_sheet_questions(self, sheet):
        number = sheet.sheet_number
        for rec_zestawy_dbf in self.zestawy_dbf:
            if number == int(rec_zestawy_dbf['NR_ZESTAWU']):
                question = self.get_or_create_question(rec_zestawy_dbf)
                sheet_questions = SheetQuestions()
                sheet_questions.question_id = question
                sheet_questions.sheet_id = sheet
                sheet_questions.order_number = int(rec_zestawy_dbf['NR_KOLEJNY'])
                sheet_questions.answer_order = rec_zestawy_dbf['KOLEJNOSC'].decode('windows-1250')
                sheet_questions.save()

    def get_or_create_question(self, rec_zestawy_dbf):
        question_number = int(rec_zestawy_dbf['NR_PYTANIA'])
        
        sq = SheetQuestions.objects.filter(sheet_id__test_id=self.test.id, question_id__question_number=question_number)
        if len(sq):
            question = sq[0].question_id
        else:
            question = self.save_question(rec_zestawy_dbf)

        return question

    def save_question(self, rec_zestawy_dbf):
        question = Question()
        question.question_number = int(rec_zestawy_dbf['NR_PYTANIA'])
        question.a_points = int(rec_zestawy_dbf['PUNKTY_A'])
        question.b_points = int(rec_zestawy_dbf['PUNKTY_B'])
        question.c_points = int(rec_zestawy_dbf['PUNKTY_C'])
        question.d_points = int(rec_zestawy_dbf['PUNKTY_D'])
        question.e_points = int(rec_zestawy_dbf['PUNKTY_E'])
        question.f_points = int(rec_zestawy_dbf['PUNKTY_F'])
        question.save()

        return question
   
    def close_dbf_files(self):
        self.testy_dbf.close()
        self.testy_dbf = None

        self.zestawy_dbf.close()
        self.zestawy_dbf = None
