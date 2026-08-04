from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from apps.loyalty.services import DashboardService


@login_required
def dashboard(request):
    context = DashboardService.build_context(request.user)
    return render(request, 'users/dashboard.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a) à B10.')
            return redirect('catalog')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
