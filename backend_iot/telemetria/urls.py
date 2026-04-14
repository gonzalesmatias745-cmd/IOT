from django.urls import path
from .views import ingesta, estado_actual, reporte_servidor

urlpatterns = [
    path('ingesta/', ingesta),
    path('estado-actual/', estado_actual),
    path('reporte-servidor/<str:id_servidor>/', reporte_servidor),
]