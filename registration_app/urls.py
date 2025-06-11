from django.urls import path
from .views import register, IndexView, edit_profile
from django.contrib.auth import views as auth_views  # сюда встроены LoginView и LogoutView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration_app/login.html', next_page='profile'),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]