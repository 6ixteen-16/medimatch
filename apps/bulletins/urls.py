from django.urls import path
from . import views

app_name = 'bulletins'

urlpatterns = [
    path('',              views.bulletin_list_view,    name='list'),
    path('create/',       views.bulletin_create_view,  name='create'),
    path('<int:pk>/',     views.bulletin_detail_view,  name='detail'),
    path('<int:pk>/edit/', views.bulletin_update_view,  name='edit'),
    path('<int:pk>/publish/', views.bulletin_publish_view, name='publish'),
    path('<int:pk>/notify/',  views.bulletin_notify_view,  name='notify'),
]
