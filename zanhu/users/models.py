# _*_ coding:utf-8 _*_
# __author__ = '__lujiawei__'

from __future__ import unicode_literals
from six import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

@python_2_unicode_compatible
class User(AbstractUser):
    """Default user for zanhu."""

    #: First and last name do not cover name patterns around the globe
    nickname = models.CharField(verbose_name='昵称', blank=True, null=True, max_length=255)
    job_title = models.CharField(verbose_name='职称', blank=True, null=True, max_length=50)
    introduction = models.TextField(verbose_name='简介', blank=True, null=True)
    picture = models.ImageField(verbose_name='头像', upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(verbose_name='城市', blank=True, null=True, max_length=50)
    personal_url = models.URLField(verbose_name='个人链接', blank=True, null=True, max_length=255)
    weibo = models.URLField(verbose_name='微博链接', blank=True, null=True, max_length=255)
    zhihu = models.URLField(verbose_name='知乎链接', blank=True, null=True, max_length=255)
    github = models.URLField(verbose_name='GitHub链接', blank=True, null=True, max_length=255)
    linkedin = models.URLField(verbose_name='领英链接', blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_profile_name(self):
        return self.nickname if self.nickname else self.username

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
