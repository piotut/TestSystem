#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dbfpy import dbf

from testownik.models import Student

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
