from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View, DetailView

from testownik.models import Student, Sheet


class IndexView(View):

	template_name = 'testownik/index.html'

	def get(self, request):
		return render(request, self.template_name)


class ChooseTestView(DetailView):

	template_name = 'testownik/choose_test.html'
	queryset = Sheet.objects.get(student_id=1)
	context_object_name = 'sheet_list'
	print queryset.test_id.start_time

	def get(self, request):
		return render(request, self.template_name)