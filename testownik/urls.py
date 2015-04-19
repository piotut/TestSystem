from django.conf.urls import url

from .views import IndexView, ChooseTestView, LoginView, SheetView, UploadFileView, UserCreationView, PdfGeneratorView
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^([0-9]+)/$', ChooseTestView.as_view(), name='choose_test'),
    url(r'^([0-9]+)/([0-9]+)/$', SheetView.as_view(), name='sheet'),
    url(r'^help/$', TemplateView.as_view(template_name='testownik/help.html'), name='help'),
    url(r'^upload/$', UploadFileView.as_view(), name='upload'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^create/$', UserCreationView.as_view(), name='create_user'),
    url(r'^pdf/([0-9]+)/([0-9]+)/$', PdfGeneratorView.as_view(), name='pdf')
]