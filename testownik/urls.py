from django.conf.urls import url

from .views import IndexView, ChooseTestView, LoginView, SheetView
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^([0-9]{5})/$', ChooseTestView.as_view(), name='choose_test'),
    url(r'^([0-9]{5})/([0-9]+)/$', SheetView.as_view(), name='sheet'),
    url(r'^help/$', TemplateView.as_view(template_name='testownik/help.html'), name='help'),
    url(r'^login/$', LoginView.as_view(template_name='testownik/login.html'), name='login'),
]