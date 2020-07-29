from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone

from .forms import TodoForm
from .models import Todo
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')

            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'Username has already been taken!'})
        else:
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Password did not match!'})

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Bad data!'})

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-id')
    return render(request, 'todo/current.html', {'todos':todos})

@login_required
def completedtodo(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodo.html', {'todos':todos})


def loginuser(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password did not match!'})
        else:
            login(request, user)
            return redirect('home')

@login_required
def logoutuser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')

@login_required
def viewtodo(request, todo_pk):
    details = get_object_or_404(Todo, pk = todo_pk, user = request.user)
    if request.method == 'GET':
        form = TodoForm(instance=details)
        return render(request, 'todo/tododetails.html', {'details': details, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=details)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/tododetails.html',
                          {'form': UserCreationForm(), 'error': 'Bad data!'})

@login_required
def completetodo(request, todo_pk):
    details = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    details.datecompleted = timezone.now()
    details.save()
    return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    details = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    details.datecompleted = timezone.now()
    details.delete()
    return redirect('currenttodos')