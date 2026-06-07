from django.urls import path
from . import views

app_name = 'donors'

urlpatterns = [
    path('',                 views.donor_list_view,   name='list'),
    path('register/',        views.DonorRegistrationWizard.as_view(views.DONOR_WIZARD_FORMS), name='register'),
    path('my-profile/',      views.my_profile_view,   name='my_profile'),
    path('<int:pk>/',        views.donor_detail_view, name='detail'),
    path('<int:pk>/approve/', views.donor_approve_view, name='approve'),
    path('<int:pk>/flag/',    views.donor_flag_view,    name='flag'),
    path('search/',          views.donor_list_view,   name='search'),
]
