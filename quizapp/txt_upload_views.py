from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
import os

"""
	format of txt file:	#no unnecessary spaces
		quiz title
		number of questions
		question title
		question text
		choice,choice,choice
		question title
		question text
        question time
		choice one,choice two,choice three
        0,1,0
"""


def make_quiz(title, questions):
    quiz = Quiz()
    quiz.title = title
    quiz.save()

    for q in questions:
        question = Question()
        question.title = q[0]
        question.question_text = q[1]
        question.time = q[2]
        question.quiz = quiz
        question.save()
        for i in range(len(q[3])):
            c = q[3][i]
            choice = Choice()
            choice.choice_text = c
            choice.question = question
            choice.is_correct = q[4][i]
            choice.save()
    return


def file_information_extract(f):
    quiz_title = f.readline().rstrip()
    num_q = int(f.readline())
    for _ in range(num_q):
        question_title = f.readline().rstrip()
        question_text = f.readline().rstrip()
        question_time = int(f.readline().rstrip())
        choices = f.readline().rstrip().split(',')
        correct_ans = bool(f.readline().rstrip().split(','))
        yield quiz_title, question_title, question_text, question_time, choices, correct_ans


@login_required
def upload_quiz(request):
    if(request.method == "POST"):
        txt_file = request.FILES['filename']
        path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "media/a.txt")
        with open(path, "wb") as a:
            for chunk in txt_file.chunks():
                a.write(chunk)
        with open(path) as a:
            quiz_title = ""
            questions = []
            for quiz_t, qt, qtext, qtime, choices, correct_ans in file_information_extract(a):
                quiz_title = quiz_t
                questions.append([qt, qtext, qtime, choices, correct_ans])
            make_quiz(quiz_title, questions)
        return redirect('homepage')
    return render(request, 'quizapp/quiz_txt_upload.html')
