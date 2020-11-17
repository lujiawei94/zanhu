from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from zanhu.messager.models import Message
from zanhu.helpers import ajax_required


class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messager/message_list.html'
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesListView, self).get_context_data()
        # 获取除登录用户外的所有用户，按最近登录时间降序排列
        context['users_list'] = get_user_model().objects.filter(is_active=True).exclude(
            username=self.request.user
        ).order_by('-last_login')[:10]
        last_conversation = Message.objects.get_most_recent_conversation(self.request.user)
        context['active'] = last_conversation.username
        return context

    def get_queryset(self):
        """最近私信互动内容"""
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(self.request.user, active_user)

class ConversationListView(MessagesListView):

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        context['active'] = self.kwargs['username']  # url传过来的'username'
        return context

    def get_queryset(self):
        active_user = get_object_or_404(get_user_model(), username=self.kwargs['username'])
        return Message.objects.get_conversation(self.request.user, active_user)


@login_required
@ajax_required
@require_http_methods(['POST'])
def send_message(request):
    sender = request.user
    recipient_username = request.POST['to']
    recipient = get_user_model().objects.get(username=recipient_username)
    message = request.POST['message']
    if len(message.strip()) != 0 and sender != recipient:
        msg = Message.objects.create(
            sender=sender,
            recipient=recipient,
            message=message,
        )
        return render(request, 'messager/single_message.html', {'message': msg})
    return HttpResponse()


@login_required
@ajax_required
@require_http_methods(['POST'])
def receive_message(request):
    message_id = request.GET['message_id']
    msg = Message.objects.get(pk=message_id)
    return render(request, 'messager/single_message.html', {'message': msg})

