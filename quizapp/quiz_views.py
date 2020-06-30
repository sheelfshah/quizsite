from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone


@login_required
def create_quiz(request):
    if(request.method == "POST"):
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_date = timezone.now()
            quiz.save()
            return redirect('add_question', primkey=quiz.pk)
    else:
        form = QuizForm()
    return render(request, 'quizapp/quiz_new.html', {'form': form})


@login_required
def edit_quiz(request, primkey):
    quiz = get_object_or_404(Quiz, pk=primkey)
    if(request.method == "POST"):
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_date = timezone.now()
            quiz.save()
            return redirect('add_question', primkey=quiz.pk)
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quizapp/quiz_new.html', {'form': form, "questions": quiz.questions.all()})


@login_required
def add_question(request, primkey):
    quiz = get_object_or_404(Quiz, pk=primkey)
    if(request.method == "POST"):
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.quiz = quiz
            q.save()
            return redirect('add_choice', primkey=q.pk)
    else:
        form = QuestionForm()
    return render(request, 'quizapp/question_edit.html', {'form': form, "questions": quiz.questions.all(), "quiz": quiz})


@login_required
def edit_question(request, primkey):
    q = get_object_or_404(Question, pk=primkey)
    if(request.method == "POST"):
        form = QuestionForm(request.POST, instance=q)
        if form.is_valid():
            q = form.save(commit=False)
            q.save()
            return redirect('add_choice', primkey=q.pk)
    else:
        form = QuestionForm(instance=q)
    return render(request, 'quizapp/question_edit.html', {'form': form, "questions": q.quiz.questions.all(), "quiz": q.quiz})


@login_required
def add_choice(request, primkey):
    q = get_object_or_404(Question, pk=primkey)
    if(request.method == "POST"):
        form = ChoiceForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.question = q
            c.save()
            return redirect('add_choice', primkey=q.pk)
    else:
        form = ChoiceForm()
    return render(request, 'quizapp/choice_edit.html', {'form': form, "choices": q.choices.all(), "question": q})


@login_required
def edit_choice(request, primkey):
    c = get_object_or_404(Choice, pk=primkey)
    if(request.method == "POST"):
        form = ChoiceForm(request.POST, instance=c)
        if form.is_valid():
            c = form.save(commit=False)
            c.save()
            return redirect('add_choice', primkey=c.question.pk)
    else:
        form = ChoiceForm(instance=c)
    return render(request, 'quizapp/choice_edit.html', {'form': form, "choices": c.question.choices.all(), "question": c.question})
