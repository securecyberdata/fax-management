from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard, name='dashboard'),
    path('single-fax/',views.new, name='new'),
    path('genknee', views.genknee, name='genknee'),
    path('sendfax/',views.sendfax, name='sendfax'),
    path('invoice/',views.geninvoice, name='geninvoice'),
    path('fax_list/', views.fax_list, name='fax_list'),
    path('fax_detail/<str:fax_id>/',views.fax_detail, name='fax_detail'),
    path('fax_resend/<str:fax_id>/', views.fax_resend, name='fax_resend'),
    path('bulk-fax/', views.bulk_fax_generator, name='bulk_fax_generator'),
    path('bulk-fax/send/', views.bulk_fax_sender, name='bulk_fax_sender'),
    	path('test-humblefax/', views.test_humblefax_connection, name='test_humblefax_connection'),
	path('single-sms/', views.single_sms, name='single_sms'),
	path('bulk-sms/', views.bulk_sms, name='bulk_sms'),
	path('test-twilio/', views.test_twilio_connection, name='test_twilio_connection'),
]
