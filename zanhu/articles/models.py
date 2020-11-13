from __future__ import unicode_literals
from six import python_2_unicode_compatible
from slugify import slugify
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from django.db import models
from django.conf import settings


@python_2_unicode_compatible
class ArticleQuerrySet(models.query.QuerySet):
    """自定义queryset api，提高模型类的可用性"""

    def get_published(self):
        """获取发表的文章"""
        return self.filter(status='P')

    def get_drafts(self):
        """获取草稿箱文章"""
        return self.filter(status='D')

    def get_counted_tags(self):
        """统计所有发表文章中，每个标签的数量>0"""
        tag_dict = {}
        query = self.get_published().annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


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
    content = MarkdownxField(verbose_name='内容')
    edited = models.BooleanField(default=False, verbose_name='是否可编辑')
    tags = TaggableManager(help_text='多个标签用,(英文)隔开', verbose_name='标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = ArticleQuerrySet.as_manager()

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        ordering = ('created_at',)

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.title)
        super(Article, self).save()

    def get_markdown(self):
        """将Markdown文本转化成html"""
        return markdownify(self.content)

