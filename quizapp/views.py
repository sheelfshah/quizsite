from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import ProfileForm, UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


def index(request):
    quizzes = Quiz.objects.order_by('-created_date')
    return render(request, "quizapp/homepage.html", {"quizzes": quizzes})


def register(request):
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('homepage')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'quizapp/register.html', {'user_form': user_form, 'profile_form': profile_form})


def login_user(request):
    if(request.method == "POST"):
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid = authenticate(username=username, password=password)
        if valid:
            login(request, valid)
            return redirect('homepage')
        else:
            return redirect('login_false')
    else:
        form = UserForm()
        return render(request, 'quizapp/login.html', {'user_form': form})


def false_login(request):
    return render(request, 'quizapp/false_login.html', {})


@login_required
def logout_user(request):
    logout(request)
    return redirect('homepage')


@login_required
def leaderboard(request):
    profiles = Profile.objects.all().order_by("-score")
    return render(request, "quizapp/leaderboard.html", {"profiles": profiles})
