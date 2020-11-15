from django.urls import reverse_lazy, resolve
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView, CreateView

from zanhu.helpers import ajax_required
from zanhu.qa.models import Question, Answer
from zanhu.qa.forms import QuestionForm


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


class AnsweredQuestionListView(QuestionListView):
    """已有采纳答案的问题"""

    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data()
        context['active'] = 'answered'
        return context


class UnansweredQuestionListView(QuestionListView):
    """已有采纳答案的问题"""

    def get_queryset(self):
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UnansweredQuestionListView, self).get_context_data()
        context['active'] = 'unanswered'
        return context


class CreateQuestionView(LoginRequiredMixin, CreateView):
    """用户提问"""

    form_class = QuestionForm
    template_name = 'qa/question_form.html'
    message = "问题已提交！"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateQuestionView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:unanswered_q')


class QuestionDetailView(LoginRequiredMixin, DetailView):
    """问题详情页"""
    model = Question
    context_object_name = 'question'
    template_name = 'qa/question_detail.html'


