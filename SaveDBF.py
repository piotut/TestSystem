#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbfpy import dbf

from testownik.models import Student, Test, Sheet

def save_students(path):
    db = dbf.Dbf(path)
    for record in db:
        index_number = int(record['NR_ALBUMU'])
        if index_number == 0:
            continue
        student_exists = Student.objects.filter(index_number=index_number).count()
        if not student_exists:
            first_name = record['IMIE'].decode('windows-1250')
            last_name = record['NAZWISKO'].decode('windows-1250')

            s = Student()
            s.first_name = first_name
            s.last_name = last_name
            s.index_number = index_number
            s.save()
    db.close()


def save_sheets(path, testId):
    try:
        db = dbf.Dbf(path)
        test = Test.objects.get(id=testId)
    except Test.DoesNotExist:
        print u"Test nie istnieje!"
    except Test.MultipleObjectReturned:
        print u"Wiele testów o danym ID"
    else:
        for record in db:
            index_number = int(record['NR_ALBUMU'])
            try:
                student = Student.objects.get(index_number=index_number)
                print student
            except Student.DoesNotExist:
                print u"Student NIE ISTNIEJE W BAZIE!"
                continue
            except Student.MultipleObjectReturned:
                print u"Wiele wpisów o tym samym numerze indeksu"
                continue
            else:
                number = int(record['NR_ZESTAWU'])

                sheet = Sheet()
                sheet.test_id = test
                sheet.student_id = student
                sheet.sheet_number = number
                sheet.save()
    finally:
        db.close()
