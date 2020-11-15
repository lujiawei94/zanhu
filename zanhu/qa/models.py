from __future__ import unicode_literals

from collections import Counter
from six import python_2_unicode_compatible
from slugify import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from taggit.managers import TaggableManager
import uuid

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey


class Vote(models.Model):
    """使用django中的contentType，创建genericForeignKEY, 同时关联多个表（用户的问题和回答的投票）"""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qa_vote', verbose_name='用户')
    value = models.BooleanField(default=True, verbose_name='是否赞同')
    #  genericForeignKey的设置
    content_type = models.ForeignKey(ContentType, related_name='votes_on', on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    votes = GenericForeignKey('content_type', 'object_id')  # 入参为缺省值

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '投票'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'content_type', 'object_id')  # 联合唯一键
        # SQL优化
        index_together = ('content_type', 'object_id')  # 联合唯一索引

@python_2_unicode_compatible
class QuestionQuerrySet(models.query.QuerySet):
    """自定义queryset api，提高模型类的可用性"""

    def get_answered(self):
        """获取已有答案的问题"""
        return self.filter(has_answer=True)

    def get_unanswered(self):
        """获取未被回答的问题"""
        return self.filter(has_answer=False)

    def get_drafts(self):
        """获取草稿问题"""
        return self.filter(status='D')

    def get_counted_tags(self):
        """统计所有标签的数量（>0）"""
        tag_dict = {}
        query = self.all().annotate(tagged=models.Count('tags')).filter(tags__gt=0)
        for obj in query:
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):

    STATUS = (
        ('O', 'Open'),
        ('C', 'Close'),
        ('D', 'Draft'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='q_author', verbose_name='提问者')
    title = models.CharField(max_length=255, unique=True, verbose_name='标题')
    slug = models.SlugField(max_length=255, verbose_name='(URL)别名')
    status = models.CharField(max_length=1, choices=STATUS, default='O', verbose_name='问题状态')
    content = MarkdownxField(verbose_name='内容')
    tags = TaggableManager(help_text='多个标签用,(英文)隔开', verbose_name='标签')
    has_answer = models.BooleanField(default=False, verbose_name='接受回答')
    votes = GenericRelation(Vote, verbose_name='投票情况')  # 通过GenericRelation关联到Vote表定义的GenericForeignKey，vote本身不是实际的字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = QuestionQuerrySet.as_manager()

    class Meta:
        verbose_name = '问题'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
           self.slug = slugify(self.title)
        super(Question, self).save(*args, **kwargs)

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """得票数"""
        dic = Counter(self.votes.values_list('value', flat=True))
        return dic[True] - dic[False]

    def get_answers(self):
        """所有回答"""
        return Answer.objects.filter(question=self)

    def count_answers(self):
        """总回答数"""
        return self.get_answers.count()

    def get_upvoters(self):
        """赞成的人"""
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """反对的人"""
        return [vote.user for vote in self.votes.filter(value=False)]

    def get_accepted_answer(self):
        """获取被接受的答案"""
        return Answer.objects.get(question=self, is_answer=True)


@python_2_unicode_compatible
class Answer(models.Model):
    uudi_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, max_length=255, related_name='a_author',
                             on_delete=models.CASCADE, verbose_name='回答者')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='问题')  # ?
    content = MarkdownxField(verbose_name='内容')
    is_answer = models.BooleanField(default=False, verbose_name='回答是否被接受')
    votes = GenericRelation(Vote, verbose_name='投票情况')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ('-is_answer', '-created_at')
        verbose_name = '答案'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:20]

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """得票数"""
        dic = Counter(self.votes.values_list('value', flat=True))
        return dic[True] - dic[False]

    def get_upvoters(self):
        """赞成的人"""
        return [vote.user for vote in self.votes.filter(value=True)]

    def get_downvoters(self):
        """反对的人"""
        return [vote.user for vote in self.votes.filter(value=False)]

    def accept_answer(self):
        """接受回答"""
        answer_set = Answer.objects.filter(question=self.question)  # 查询当前问题的所有回答
        answer_set.update(is_answer=False)  # 全部置为未接受
        # 然后再接受当前回答
        self.is_answer = True
        self.save()
        self.question.has_answer = True
        self.save()


"""
1.对于需要返回查询集的逻辑，写在QuerySetModel中
2.模型中数据库处理的逻辑写在Model中
3.对于业务逻辑相关处理写在Views中
"""
