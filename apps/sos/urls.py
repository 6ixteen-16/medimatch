from django.urls import path
from . import views

app_name = 'sos'

urlpatterns = [
    path('',                    views.sos_list_view,        name='list'),
    path('create/',             views.sos_create_view,      name='create'),
    path('active/',             views.sos_active_partial,   name='active_partial'),
    path('<int:pk>/',           views.sos_detail_view,      name='detail'),
    path('<int:pk>/acknowledge/', views.sos_acknowledge_view, name='acknowledge'),
    path('<int:pk>/transit/',   views.sos_transit_view,     name='transit'),
    path('<int:pk>/resolve/',   views.sos_resolve_view,     name='resolve'),
    path('<int:pk>/cancel/',    views.sos_cancel_view,      name='cancel'),
]
