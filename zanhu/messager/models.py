from __future__ import unicode_literals
from six import python_2_unicode_compatible
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model


class MessageQuerySet(models.query.QuerySet):

    def get_conversation(self, sender, recipient):
        qs_one = self.filter(sender=sender, recipient=recipient)
        qs_two = self.filter(sender=recipient, recipient=sender)
        return qs_one.union(qs_two).order_by('created_at')

    def get_most_recent_conversation(self, recipient):
        try:
            qs_sent = self.filter(sender=recipient)  # 当前登录用户发送的消息
            qs_received = self.filter(recipient=recipient)  # 当前登录用户接收的消息
            qs = qs_received.union(qs_sent).latest('created_at')  # 最新的对话
            if qs.sender == recipient:
                return qs.recipient  # 登录用户发送的则返回接受者
            return qs.sender  # 非登录用户发送，则返回该发送用户
        except self.model.DoesNotExist:
            return get_user_model().objects.get(username=recipient.username)  # 当不存在私信（收发）记录时返回当前用户


class Message(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages',
                               blank=True, null=True, on_delete=models.SET_NULL, verbose_name='发送者')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages',
                                  blank=True, null=True, on_delete=models.SET_NULL, verbose_name='接收者')
    message = models.TextField(blank=True, null=True, verbose_name='消息')
    unread = models.BooleanField(default=True, db_index=True, verbose_name='是否未读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    objects = MessageQuerySet.as_manager()

    class Meta:
        verbose_name = '私信'
        verbose_name_plural = verbose_name
        ordering = ('created_at',)

    def __str__(self):
        return self.message

    def make_as_read(self):
        if self.unread:
            self.unread = False
            self.save()
