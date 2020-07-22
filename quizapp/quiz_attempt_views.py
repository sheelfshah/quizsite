from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, Profile, Quiz
from .forms import QuizForm, QuestionForm, ChoiceForm, AttemptForm
from django.contrib.auth.decorators import login_required


@login_required
def attempt_quiz(request, primkey):
    quiz = get_object_or_404(Quiz, pk=primkey)
    questions = quiz.questions.all()
    if(request.method == "POST"):
        return redirect('attempt_question', primkey=questions[0].pk)
    else:
        return render(request, 'quizapp/attempt_quiz.html', {"quiz": quiz, "question": questions[0], "length": len(questions)})


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
    if request.user in question.attempters.all():
        prev_attempt = True
    question.attempters.add(request.user)
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
    if(request.method == "POST"):
        form = AttemptForm(choices, request.POST)
        if form.is_valid():
            temp = form.cleaned_data.get("options")
            for c_pk in temp:
                choice = get_object_or_404(Choice, pk=c_pk)
                choice.choosers.add(request.user)
                choice.votes += 1
                choice.save()
        if q_next_id == 0:
            return redirect('quiz_end', primkey=quiz.pk)
        else:
            return redirect('attempt_question', primkey=q_next_id)
    else:
        form = AttemptForm(choices)
    return render(request, 'quizapp/attempt_question.html', {"form": form, "question": question,
                                                             "next": q_next_id, "attempted": prev_attempt,
                                                             "time": question.time, "marks": question.marks})
