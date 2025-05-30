from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import CustomerUserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView  # для отображения простых HTML-шаблонов без дополнительной логики.
from django.db import IntegrityError  # исключение (exception), которое выбрасывается при нарушении ограничений
# целостности базы данных.


class IndexView(TemplateView):
    template_name = 'registration_app/index.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'registration_app/profile.html'
    login_url = reverse_lazy('login')


def register(request):
    if request.method == 'POST':
        form = CustomerUserCreationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('login')
            except IntegrityError:
                form.add_error('username', 'Пользователь с таким именем уже существует')
    else:
        form = CustomerUserCreationForm()  # пустая форма при заходе в первый раз
    return render(request, 'registration_app/register.html', {'form': form})


def profile(request):
    user = request.user
    email = user.email
    first_name = user.first_name
    last_name = user.last_name

    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name
    }

    return render(request, 'registration_app/profile.html', {'context': context})