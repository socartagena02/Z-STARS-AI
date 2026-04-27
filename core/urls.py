from django.contrib import admin
from django.urls import path
from games import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', views.index, name='iniciosesion'),
    path('memorice/', views.memorice, name='memorice'),
    path('simon_dice/', views.simon_dice, name='simon_dice'),
    path('api/test/', views.lista_partida, name="test_api"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('puntos/', views.puntos, name="puntos"),
    path('menu_juegos', views.menuJuegos, name="menu_juegos"),
    path('logout', views.logout, name="logout"),
    path('api/analizar/', views.analisis, name='analisis'),
    path('registro/', views.registro, name='registro'),
]
