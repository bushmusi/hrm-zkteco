from django.conf.urls import url
from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [

    path('user-data', views.user_data),
    path('att-list', views.attendance_list),
    path('att-live-capture', views.attendance_live_capture),
    path('refresh/att/plant/1',views.plant_01_att),
    path('refresh/att/plant/2',views.plant_02_att),
    path('refresh/meal/plant/1',views.plant_01_meal),
    path('refresh/meal/plant/2',views.plant_02_meal)

]

urlpatterns = format_suffix_patterns(urlpatterns)
