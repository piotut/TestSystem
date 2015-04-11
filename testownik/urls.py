from django.conf.urls import url

from .views import IndexView, ChooseTestView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^test/$', ChooseTestView.as_view(), name='choose_test'),
]