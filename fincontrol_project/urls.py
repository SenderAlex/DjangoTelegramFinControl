from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('fincontrol_app.urls', namespace='fincontrol_app')),
    path('', include('registration_app.urls')),
]
