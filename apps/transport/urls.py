from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    path('',                          views.transport_list_view,     name='list'),
    path('create/<int:donor_id>/',    views.transport_create_view,   name='create'),
    path('<int:pk>/approve/',         views.transport_approve_view,  name='approve'),
    path('<int:pk>/complete/',        views.transport_complete_view, name='complete'),
]
