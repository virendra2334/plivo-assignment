from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^inbound/sms/$', views.InboundSMSView.as_view(), name="inbound_sms"),
    url(r'^outbound/sms/$', views.OutboundSMSView.as_view(), name="outbound_sms"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
