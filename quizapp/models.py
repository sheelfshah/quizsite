from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    email = models.EmailField(max_length=254)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    evaluated_users = models.ManyToManyField(
        User, related_name="evaluated_quizzes")

    def __str__(self):
        return self.title

    def publish(self):
        self.published_date = timezone.now()
        self.save()


class Question(models.Model):
    title = models.CharField(max_length=100)
    question_text = models.CharField(max_length=1000)
    time = models.IntegerField(default=60)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="questions")
    attempters = models.ManyToManyField(
        User, related_name="attempted_questions")

    def __str__(self):
        return self.title


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices")
    choosers = models.ManyToManyField(User, related_name="chosen_choices")
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text
