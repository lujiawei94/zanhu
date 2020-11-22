from asgiref.sync import async_to_sync

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.template.loader import render_to_string
from django.contrib import messages

from channels.layers import get_channel_layer

from zanhu.notifications.models import Notification
from zanhu.helpers import ajax_required


class NotificationUnreadListView(LoginRequiredMixin, ListView):
    model = Notification
    context_object_name = 'notification_list'
    template_name = 'notifications/notification_list.html'

    def get_queryset(self, **kwargs):
        return self.request.user.notifications.unread()

@login_required
def mark_all_as_read(request):
    request.user.notifications.mark_all_as_read()
    redirect_url = request.GET.get('next')
    messages.add_message(request, messages.SUCCESS, f'用户{request.user.username}的所有通知标记为已读')
    return redirect(redirect_url) if redirect_url else redirect('notifications:unread')

@login_required
def mark_as_read(request, slug):
    notification = get_object_or_404(Notification, slug=slug)
    notification.mark_as_read()
    redirect_url = request.GET.get('next')
    messages.add_message(request, messages.SUCCESS, f'通知{notification}标为已读')
    return redirect(redirect_url) if redirect_url else redirect('notifications:unread')

@login_required
def get_latest_notifications(request):
    notifications = request.user.notifications.get_most_recent()
    return render(request, 'notifications/most_recent.html',
                  {'notifications': notifications})


def notification_handler(actor, recipient, verb, action_object, **kwargs):
    """
    通知处理器
    :param actor:           request.user对象
    :param recipient:       User Instance 接收者实例，可以是一个或者多个接收者
    :param verb:            str 通知类别
    :param action_object:   Instance 动作对象的实例
    :param kwargs:          key, id_value等
    :return:                None
    """
    key = kwargs.get('key', 'notification')
    id_value = kwargs.get('id_value', None)
    # 记录通知内容
    Notification.objects.create(
        actor=actor,
        recipient=recipient,
        verb=verb,
        action_object=action_object
    )

    channel_layer = get_channel_layer()
    payload = {
        'type': 'receive',
        'key': key,
        'actor_name': actor.username,
        'action_object': action_object.user.username,
        'id_value': id_value
    }
    async_to_sync(channel_layer.group_send)('notifications', payload)

