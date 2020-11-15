from django.urls import path

from zanhu.qa import views

app_name = 'qa'

urlpatterns = [
    path('', views.UnansweredQuestionListView.as_view(), name='unanswered_q'),
    path('answered/', views.AnsweredQuestionListView.as_view(), name='answered_q'),
    path('indexed/', views.QuestionListView.as_view(), name='all_q'),
    path('ask-question/', views.CreateQuestionView.as_view(), name='ask_question'),
    path('question-detail/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
]
