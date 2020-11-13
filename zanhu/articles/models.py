from __future__ import unicode_literals
from six import python_2_unicode_compatible

from django.db import models
from django.conf import settings


@python_2_unicode_compatible
class Article(models.Model):

    STATUS = (
        ('D', 'Draft'),
        ('P', 'Published')
    )
    title = models.CharField(max_length=255, unique=True, verbose_name='标题')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='author', verbose_name='作者')
    image = models.ImageField(upload_to='articles_pictures/%Y/%m/%d', verbose_name='文章图片')
    slug = models.SlugField(max_length=255, verbose_name='(URL)别名')
    status = models.CharField(max_length=1, choices=STATUS, default='D', verbose_name='状态')
    content = models.TextField(verbose_name='内容')
    edited = models.BooleanField(default=False, verbose_name='是否可编辑')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ('created_at',)

    def __str__(self):
        return self.title
