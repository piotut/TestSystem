#!/usr/bin/env python
# -*- coding: utf-8 -*-

from testownik.models import Sheet, SheetQuestions, Results, Question

class TestResults(object):
    def __init__(self, answers, sheet_id):
        self.answers = answers
        self.sheet_id = sheet_id
        self.save_results()

    def get_sheet_obj(self):
        '''Zwraca aktywny arkusz dla studenta o danym indeksie'''
        sheet_list = Sheet.objects.filter(id=self.sheet_id)
        print sheet_list
        for sheet in sheet_list:
            if sheet.is_active():
                print sheet
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
            #print sq_id_list[i].question_id.id
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

        self.compare_results_and_questions(sheet)

    def _return_points_for_question(self, q_points, res):



        if not q_points and res:
            return -1
        else:
            return q_points * res


    def compare_results_and_questions(self, sheet):
        res_list = Results.objects.filter(sheet_id=sheet)
        self.points = 0

        for res in res_list:
            points = 0

            points += self._return_points_for_question(res.question_id.a_points, res.a)
            points += self._return_points_for_question(res.question_id.b_points, res.b)
            points += self._return_points_for_question(res.question_id.c_points, res.c)
            points += self._return_points_for_question(res.question_id.d_points, res.d)
            points += self._return_points_for_question(res.question_id.e_points, res.e)
            points += self._return_points_for_question(res.question_id.f_points, res.f)

            self.points += points if points > 0 else 0 

        sheet.points = self.points
        sheet.save()
    

class TestAnswers(object):
    "Odpowiedzi udzielone przez studenta"
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id

    def get_answers(self):
        map_answer = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F'}
        sheet = Sheet.objects.get(id=self.sheet_id)
        results = Results.objects.filter(sheet_id=sheet)
        response = []
        for res in results:
            sq = SheetQuestions.objects.get(question_id=res.question_id, sheet_id=sheet)
            order = list(sq.answer_order)
            #print sq.answer_order
            #print res.a, res.b, res.c, res.d
            answers = ''
            correct = ''
            if res.a:
                answers += map_answer[order.index('1')]
            if res.b:
                answers += map_answer[order.index('2')]
            if res.c:
                answers += map_answer[order.index('3')]
            if res.d:
                answers += map_answer[order.index('4')]
            if res.e:
                answers += map_answer[order.index('5')]
            if res.f:
                answers += map_answer[order.index('6')]

            if res.question_id.a_points:
                correct += map_answer[order.index('1')]
            if res.question_id.b_points:
                correct += map_answer[order.index('2')]
            if res.question_id.c_points:
                correct += map_answer[order.index('3')]
            if res.question_id.d_points:
                correct += map_answer[order.index('4')]
            if res.question_id.e_points:
                correct += map_answer[order.index('5')]
            if res.question_id.f_points:
                correct += map_answer[order.index('6')]
            
            response.append({'answers': answers, 'correct': correct})

        return response
