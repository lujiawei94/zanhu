# _*_ coding:utf-8 _*_

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    template_name = 'users/user_detail.html'
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data()
        user = User.objects.get(username=self.request.user.username)
        context['moments_num'] = user.publisher.filter(reply=False).count()
        context['article_num'] = user.author.filter(status='P').count()
        context['comment_num'] = user.publisher.filter(reply=True).count() + user.comment_comments.all().count()
        context['question_num'] = user.q_author.all().count()
        context['answer_num'] = user.a_author.all().count()

        tem = set()
        sent_num = user.sent_messages.all()
        for s in sent_num:
            tem.add(s.recipient.username)
        received_num = user.received_messages.all()
        for r in received_num:
            tem.add(r.sender.username)
        context['interaction_num'] = user.liked_news.all().count() + user.qa_vote.all().count() + \
        context['comment_num'] + len(tem)

        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ['nickname', 'job_title', 'introduction', 'picture', 'location', 'personal_url', 'weibo', 'zhihu', 'github', 'linkedin']
    template_name = 'users/user_form.html'
    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

