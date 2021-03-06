from django.urls import path

from . import views
from . import quiz_views
from . import quiz_attempt_views, quiz_result_views, txt_upload_views

urlpatterns = [
    path('', views.index, name='homepage'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('login_retry/', views.false_login, name="login_false"),
    path('quiz/new', quiz_views.create_quiz, name="quiz_new"),
    path('quiz/<int:primkey>/add_question',
         quiz_views.add_question, name="add_question"),
    path('quiz/<int:primkey>/edit', quiz_views.edit_quiz, name="quiz_edit"),
    path('quiz/<int:primkey>/attempt',
         quiz_attempt_views.attempt_quiz, name="attempt_quiz"),
    path('quiz/<int:primkey>/end',
         quiz_attempt_views.submit_quiz, name="quiz_end"),
    path('quiz/<int:primkey>/evaluate',
         quiz_result_views.evaluate_quiz, name="quiz_evaluate"),
    path('quiz/<int:primkey>/analytics',
         quiz_result_views.show_analytics, name="quiz_analytics"),
    path('question/<int:primkey>/add_choice',
         quiz_views.add_choice, name="add_choice"),
    path('question/<int:primkey>/edit',
         quiz_views.edit_question, name="edit_question"),
    path('question/<int:primkey>/attempt',
         quiz_attempt_views.attempt_question, name="attempt_question"),
    path('choice/<int:primkey>/edit', quiz_views.edit_choice, name="edit_choice"),
    path('leaderboard', views.leaderboard, name="leaderboard"),
    path('quiz/upload', txt_upload_views.upload_quiz, name="quiz_txt_upload"),
    path('resetscores', views.reset_scores, name="resetscores"),
]
