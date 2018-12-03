from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic import TemplateView


class RegisterView(TemplateView):
    template_name = 'auth/register.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if username is None or password is None:
            return render(request, self.template_name, {'message': 'Both fields are required!'})
        if User.objects.filter(username=username).exists():
            return render(request, self.template_name, {"message": "Username already taken!"})
        user = User(username=username)
        user.set_password(password)
        user.save()
        return redirect('/auth/login')


@login_required
def logout_view(response):
    logout(response)
    return redirect('/')


class LoginView(TemplateView):
    template_name = "auth/login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            path = request.GET.get('next', '/')
            return redirect(path)
        else:
            return render(request, self.template_name, {'message': "Username or password not correct!"})
