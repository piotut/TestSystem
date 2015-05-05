#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testownik.models import Sheet, SheetQuestions, Results, Question

class TestResults(object):
    def __init__(self, answers, index):
        self.answers = answers
        self.index = index
        self.save_results()

    def get_sheet_obj(self):
        '''Zwraca aktywny arkusz dla studenta o danym indeksie'''
        sheet_list = Sheet.objects.filter(student_id__index_number=self.index)
        for sheet in sheet_list:
            if sheet.is_active():
                return sheet

    def get_sheetquestions_obj(self, sheet_obj):
        '''Zwraca liste obektow SheetQuestions dla danego arkusza'''
        sq_list = SheetQuestions.objects.filter(sheet_id=sheet_obj)
        return sq_list

    def return_correct_order(self, sq_list):
        map_answer = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6}
        answer_list = []
        for sq in sq_list:
            answer_order_list = list(sq.answer_order)
            answer_list.append([])
            answer_list[sq.order_number-1] = [False]*len(sq.answer_order)
            for answer in self.answers[int(sq.order_number)-1].get('choice_field', []):
                answer_list[sq.order_number-1][int(answer_order_list[map_answer[answer]-1])-1] = True

        return answer_list
        
    def _list_or_none(self, x, number):
        return x[number] if len(x) > number else False

    def save_results(self):
        sheet = self.get_sheet_obj()
        sq_list = self.get_sheetquestions_obj(sheet)
        correct_answer_list = self.return_correct_order(sq_list)
        sq_id_list = [sq_id for sq_id in sq_list]

        for i, element in enumerate(correct_answer_list):
            res = Results(
                sheet_id  = sheet,
                question_id = sq_id_list[i].question_id,
                a = self._list_or_none(element, 0),
                b = self._list_or_none(element, 1),
                c = self._list_or_none(element, 2),
                d = self._list_or_none(element, 3),
                e = self._list_or_none(element, 4),
                f = self._list_or_none(element, 5)
            )
            res.save()
