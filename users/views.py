from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import loader


@login_required
def user_main(request):
    if request.method == 'GET':
        template = loader.get_template('users/main.html')
        return HttpResponse(template.render({}, request))


def user_login(request):
    if request.method == 'GET':
        template = loader.get_template('users/login.html')
        next = request.GET.get('next', '/user/')
        return HttpResponse(template.render({'next': next}, request))
    if request.method == 'POST':
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            next = request.GET.get('next', '/user/')
            user = authenticate(request, username=username, password=password)

            if user is None:
                messages.info(
                    request, f'Login failed! please recheck your username and password!')
                return redirect(f'/user/login/?{next}')

            login(request, user)
            return redirect(next)

        except:
            messages.info(
                request, f'Login failed! please recheck your username and passwords!')
            return redirect('/user/login/')


def user_signup(request):
    if request.method == 'GET':
        template = loader.get_template('users/signup.html')
        next = request.GET.get('next', '/user/')
        return HttpResponse(template.render({'next': next}, request))
    if request.method == 'POST':
        try:
            username = request.POST["username"]
            password = request.POST["password"]
            next = request.GET.get('next', '/user/')

            User.objects.create_user(username, password=password)
            return redirect(next)

        except:
            messages.info(
                request, f'User already exist!')
            return redirect(f'/user/signup/')


@login_required
def user_logout(request):
    if request.method == 'GET':
        logout(request)
        return redirect('/user/')
