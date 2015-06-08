from django.conf.urls import url

from .views import IndexView, LoginView, SheetView, UploadFileView, UserCreationView, DeleteTestView, PdfGeneratorView, TestListView, SheetListView, ConfirmTestStartView, CSVSheetView
from django.views.generic import TemplateView

from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^([0-9]+)/$', SheetView.as_view(), name='sheet'),
    url(r'^help/$', TemplateView.as_view(template_name='testownik/help.html'), name='help'),
    url(r'^upload/$', login_required(UploadFileView.as_view()), name='upload'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': 'index'}, name='logout'),
    url(r'^create/$', UserCreationView.as_view(), name='create_user'),
    url(r'^pdf/([0-9]+)/([0-9]+)/$', PdfGeneratorView.as_view(), name='pdf'),
    url(r'^tests/$', login_required(TestListView.as_view()), name='tests'),
    url(r'^tests/([0-9]+)/$', login_required(SheetListView.as_view()), name='sheets'),
    url(r'^confirm/([0-9]+)/$', ConfirmTestStartView.as_view(), name='confirm'),
    url(r'^delete/([0-9]+)/$', login_required(DeleteTestView.as_view()), name='delete'),
    url(r'^csv/([0-9]+)/$', login_required(CSVSheetView.as_view()), name='csv'),
]
