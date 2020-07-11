import matplotlib
matplotlib.use('Agg')
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm, AttemptForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.core.files.storage import default_storage
import os
import io
import urllib
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


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
    email_text += "\t"
    email_text += str(question.marks)
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
        return render(request, "quizapp/result_page.html", {"text": email_text})
    else:
        if not quiz.published_date:
            return render(request, "quizapp/no_result.html", {})
        questions = quiz.questions.all()
        email_text = quiz.title
        email_text += "\n"
        email_text += "\n"
        num_correct = 0
        total = 0
        for question in questions:
            correct_choices, chosen_choices = evaluate_question_for_user(
                question, request.user)
            et, crrct = get_email_text(question,
                                       correct_choices, chosen_choices)
            email_text += et
            email_text += "\n"
            if crrct:
                num_correct += question.marks
            total += question.marks
        email_text += "\nYour score: \n"
        email_text += str(num_correct)
        email_text += "/"
        email_text += str(total)
        email_text += "\n"
        score = num_correct
        if not request.user in quiz.evaluated_users.all():
            request.user.profile.score += score
            request.user.profile.save()
        quiz.evaluated_users.add(request.user)
        return render(request, "quizapp/result_page.html", {"text": email_text, "score": score, "total": total})


def create_analytics(primkey, current_user):
    quiz = get_object_or_404(Quiz, pk=primkey)
    questions = quiz.questions.all()
    user_scores = {}
    total_marks = 0
    question_correct = {}
    user_correct = {}
    for question in questions:
        num_people_crrct = 0
        total_marks += question.marks
        for user in question.attempters.all():
            correct_choices, chosen_choices = evaluate_question_for_user(
                question, user)
            crrct = correct_choices == chosen_choices
            if not user.pk in user_scores.keys():
                user_scores[user.pk] = 0
            if crrct:
                user_scores[user.pk] += question.marks
                num_people_crrct += 1
            if user == current_user:
                user_correct[question.pk] = crrct
        question_correct[question.pk] = num_people_crrct / \
            len(question.attempters.all())
    return user_scores, question_correct, total_marks, user_correct


@login_required
def show_analytics(request, primkey):
    user_scores, question_correct, total_marks, user_correct = create_analytics(
        primkey, request.user)
    plt.rcParams['xtick.labelsize'] = 15
    plt.rcParams['ytick.labelsize'] = 15
    fig = plt.figure()
    fig.suptitle('Comparision of scores', fontsize=22)
    ax = fig.add_subplot(111)
    people = ['You', 'Average', 'Topper']
    score_sum = 0
    max_score = 0
    for pk, score in user_scores.items():
        score_sum += score
        max_score = max(score, max_score)
    try:
        if request.user.is_staff:
            scores = [0, score_sum / len(user_scores), max_score]
        else:
            scores = [user_scores[request.user.pk],
                      score_sum / len(user_scores), max_score]
    except:
        scores = [0, 0, 0]
    ax.bar(people, scores, color=(1, 0, 0, 0.9), edgecolor='black')
    ax.set_ylabel('Scores', fontsize=18)
    ax.set_ylim(top=total_marks * 1.1)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    # first over, second starts
    plt.rcParams['xtick.labelsize'] = 13
    fig2 = plt.figure()
    fig2.suptitle('Percent of people who answered correctly', fontsize=22)
    ax2 = fig2.add_subplot(111)
    questions = []
    qscores = []
    correctly_answered = [False] * len(question_correct.keys())
    pos = 0
    for pk, qs in question_correct.items():
        q = get_object_or_404(Question, pk=pk)
        questions.append(q.title[:3])
        qscores.append(qs * 100)
        correctly_answered[pos] = user_correct[pk]
        pos += 1
    barlist = ax2.bar(questions, qscores, color=(
        1, 0, 0, 0.9), edgecolor='black', width=0.8)
    for i in range(len(correctly_answered)):
        if correctly_answered[i]:
            barlist[i].set_facecolor((0, 1, 0, 0.9))
    ax2.set_ylabel('Accuracy %', fontsize=18)
    ax2.set_ylim(top=100)
    C = mpatches.Patch(color=(0, 1, 0, 0.9), label='Correct')
    IC = mpatches.Patch(color=(1, 0, 0, 0.9), label='Incorrect')
    ax2.legend(handles=[C, IC], loc=1, title="Your answer", fancybox=True)
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format='png')
    buf2.seek(0)
    string2 = base64.b64encode(buf2.read())
    uri2 = urllib.parse.quote(string2)
    response = render(request, "quizapp/analytics.html",
                      {"data": uri, "data2": uri2})
    plt.close(fig)
    plt.close(fig2)
    return response
