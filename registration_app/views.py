from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomerUserCreationForm, CustomUserUpdateForm
from django.views.generic import TemplateView  # для отображения простых HTML-шаблонов без дополнительной логики.
from django.db import IntegrityError  # исключение (exception), которое выбрасывается при нарушении ограничений
# целостности базы данных.


class IndexView(TemplateView):
    template_name = 'registration_app/index.html'


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


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'registration_app/profile.html', {'form': form})