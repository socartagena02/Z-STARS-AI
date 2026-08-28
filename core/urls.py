from django.contrib import admin
from django.urls import path
from games import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Páginas públicas
    path('', views.index, name='home'),
    path('login/', views.iniciosesion, name='iniciosesion'),
    path('registro/', views.registro, name='registro'),
    
    # Recuperación de contraseña
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # App
    path('dashboard/', views.dashboard, name='dashboard'),
    path('menu_juegos', views.menuJuegos, name='menu_juegos'),
    
    # Juegos
    path('memorice/', views.memorice, name='memorice'),
    path('simon_dice/', views.simon_dice, name='simon_dice'),
    path('maze/', views.maze, name='maze'),
    
    # APIs
    path('api/partidas/', views.lista_partida, name="lista_partida"),
    path('api/partidas/registrar/', views.puntos, name="puntos"),
    path('api/analizar/', views.analisis, name='analisis'),
    
    # Sesión
    path('logout', views.logout, name="logout"),
]
