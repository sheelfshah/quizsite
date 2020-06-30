from django import forms
from django.contrib.auth.models import User
from .models import *


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = {'username', 'password'}


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = {}


class QuizForm(forms.ModelForm):

    class Meta:
        model = Quiz
        fields = {'title'}


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = {'title', 'question_text'}


class ChoiceForm(forms.ModelForm):

    class Meta:
        model = Choice
        fields = {'choice_text', 'is_correct'}


class AttemptForm(forms.Form):

    def __init__(self, choices, *args, **kwargs):
        super(AttemptForm, self).__init__(*args, **kwargs)
        self.fields['options'] = forms.MultipleChoiceField(
            choices=choices, widget=forms.CheckboxSelectMultiple(), label="")
