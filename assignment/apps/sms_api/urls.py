from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import BaseView

urlpatterns = [
    url(r'^blah/$', BaseView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
