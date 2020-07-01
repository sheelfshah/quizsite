from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm, AttemptForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.files.storage import default_storage
import os


def evaluate_question_for_user(question, user):
    correct_choices = []
    chosen_choices = []
    for c in question.choices.all():
        if c.is_correct:
            correct_choices.append(c)
        if user in c.choosers.all():
            chosen_choices.append(c)
    return correct_choices, chosen_choices


def get_email_text(question, correct_choices, chosen_choices):
    email_text = ""
    email_text += question.title
    email_text += "\n"
    email_text += question.question_text
    email_text += "\n"
    if correct_choices == chosen_choices:
        email_text += "You answered correctly! \n"
    else:
        email_text += "Your answer was incorrect! \n"
    email_text += "Correct option(s): \n"
    for c in correct_choices:
        email_text += "\t"
        email_text += c.choice_text
        email_text += "\n"
    email_text += "Chosen option(s): \n"
    for c in chosen_choices:
        email_text += "\t"
        email_text += c.choice_text
        email_text += "\n"
    if len(chosen_choices) == 0:
        email_text += "\t"
        email_text += "None"
        email_text += "\n"
    return email_text, correct_choices == chosen_choices


@login_required
def evaluate_quiz(request, primkey):
    quiz = get_object_or_404(Quiz, pk=primkey)
    if request.user.is_staff:
        quiz.publish()
        questions = quiz.questions.all()
        email_text = quiz.title
        email_text += "\n"
        email_text += "\n"
        for question in questions:
            for user in question.attempters.all():
                correct_choices, chosen_choices = evaluate_question_for_user(
                    question, user)
                email_text += user.username
                email_text += "\n"
                et, crrct = get_email_text(question,
                                           correct_choices, chosen_choices)
                email_text += et
                email_text += "\n"
        filename ="/home/deepashah/deepashah.pythonanywhere.com/media/eval_quiz_" + str(quiz.pk) + "_all.txt"
        f = open(filename, "w")
        f.write(email_text)
        f.close()
        with open(filename, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(filename)
        default_storage.delete(filename)
        return response
    else:
        if not quiz.published_date:
            return render(request, "quizapp/no_result.html", {})
        questions = quiz.questions.all()
        email_text = quiz.title
        email_text += "\n"
        email_text += "\n"
        num_correct = 0
        for question in questions:
            correct_choices, chosen_choices = evaluate_question_for_user(
                question, request.user)
            et, crrct = get_email_text(question,
                                       correct_choices, chosen_choices)
            email_text += et
            email_text += "\n"
            if crrct:
                num_correct += 1
        email_text += "\nYour score: \n"
        email_text += str(num_correct)
        email_text += "/"
        email_text += str(len(questions))
        email_text += "\n"
        filename = "/home/deepashah/deepashah.pythonanywhere.com/media/eval_quiz_" + \
            str(primkey) + "_user_" + str(request.user.pk) + ".txt"
        f = open(filename, "w")
        f.write(email_text)
        f.close()
        with open(filename, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(filename)
        default_storage.delete(filename)
        return response
