from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm, AttemptForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone


@login_required
def attempt_quiz(request, primkey):
    quiz = get_object_or_404(Quiz, pk=primkey)
    questions = quiz.questions.all()
    if(request.method == "POST"):
        return redirect('attempt_question', primkey=questions[0].pk)
    else:
        return render(request, 'quizapp/attempt_quiz.html', {"quiz": quiz, "question": questions[0]})


@login_required
def submit_quiz(request, primkey):
    quiz = get_object_or_404(Quiz, pk=primkey)
    return render(request, 'quizapp/quiz_submitted.html', {"quiz": quiz})


@login_required
def attempt_question(request, primkey):
    question = get_object_or_404(Question, pk=primkey)
    quiz = question.quiz
    all_q = quiz.questions.all()
    q_next_id = 0
    q_found = False
    prev_attempt = False
    for q in all_q:
        if q.pk == primkey:
            q_found = True
            continue
        if q_found:
            q_next_id = q.pk
            break
    choices = []
    for c in question.choices.all():
        choices.append((c.pk, c.choice_text))
        if request.user in c.choosers.all():
            prev_attempt = True
    if(request.method == "POST"):
        form = AttemptForm(choices, request.POST)
        if form.is_valid():
            temp = form.cleaned_data.get("options")
            for c_pk in temp:
                choice = get_object_or_404(Choice, pk=c_pk)
                choice.choosers.add(request.user)
                choice.save()
        if q_next_id == 0:
            return redirect('quiz_end', primkey=quiz.pk)
        else:
            return redirect('attempt_question', primkey=q_next_id)
    else:
        form = AttemptForm(choices)
    return render(request, 'quizapp/attempt_question.html', {"form": form, "question": question,
                                                             "next": q_next_id, "attempted": prev_attempt})

"""
        forms = {}
        for q in questions:
            choices = []
            for c in q.choices.all():
                choices.append((c.pk, c.choice_text))
            form = QuestionAttemptForm()
            form.add_choices(choices)
            print(choices)
            form = form.create_question_attempt_form()
            forms[q.pk] = form

{% for question in questions%}
    <h3>
        {{question.title}}
    </h3>
    <h4>{{question.question_text}}</h4>
    <br>
{% endfor %}

{% for key, form in forms.items %}
    <form method="POST" class="post-form">
        {%csrf_token%}
        {{form.as_p}}
        <button type="submit" class="save-button">Submit Question</button>
    </form>
{% endfor %}
"""
