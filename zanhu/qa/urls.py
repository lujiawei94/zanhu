from django.urls import path

from zanhu.qa import views

app_name = 'qa'

urlpatterns = [
    path('indexed/', views.QuestionListView.as_view(), name='all_q'),
]
