from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',       views.dashboard_view,          name='home'),
    path('stats/', views.dashboard_stats_partial,  name='stats'),
]
