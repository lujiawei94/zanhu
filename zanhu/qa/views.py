from django.urls import reverse, resolve
from django.contrib import messages
from django.http import JsonResponse,HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView, CreateView

from zanhu.helpers import ajax_required
from zanhu.qa.models import Question, Answer


class QuestionListView(LoginRequiredMixin, ListView):
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa/question_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QuestionListView, self).get_context_data()
        context['popular_tags'] = Question.objects.get_counted_tags()  # 页面的标签功能
        context['active'] = 'all'
        return context
