from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView, UpdateView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django_comments.signals import comment_was_posted

from zanhu.articles.models import Article
from zanhu.articles.forms import ArticleForm
from zanhu.helpers import AuthorRequireMixin
from zanhu.notifications.views import notification_handler

class ArticlesListView(LoginRequiredMixin, ListView):
    """已发布的文章列表"""
    model = Article
    paginate_by = 10
    context_object_name = "articles"
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_published()

class DraftListView(ArticlesListView):
    """草稿箱文章列表"""

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user).get_drafts()


@method_decorator(cache_page(60 * 60), name='get')
class ArticleCreateView(LoginRequiredMixin, CreateView):
    """用户发表文章"""
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_create.html'
    message = '您的文章创建成功'  # 消息器指示
    initial = {'title': '文章标题初始化'}  # 固定初始化字段，get_initail 动态化

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """创建成功后跳转"""
        messages.success(self.request, self.message)  # messages 是django的消息框架， 将一条消息传递给下一次请求
        return reverse_lazy('articles:list')

    def get_initial(self):
        initial = super().get_initial()
        pass  # 动态初始化逻辑代码
        return initial


class ArticleDetailView(LoginRequiredMixin, DetailView):
    """文章详情"""
    model = Article
    template_name = 'articles/article_detail.html'

    def get_queryset(self):
        return Article.objects.select_related('user').filter(slug=self.kwargs['slug'])


class ArticleEditView(LoginRequiredMixin, AuthorRequireMixin, UpdateView):
    """文章编辑"""
    model = Article
    template_name = 'articles/article_update.html'
    message = '文章编辑成功'
    form_class = ArticleForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('articles:article', kwargs={"slug": self.get_object().slug})

def notify_comment(**kwargs):
    """文章有评论时消息通知作者"""

    actor = kwargs['request'].user
    obj = kwargs['comment'].content_object

    notification_handler(actor, obj.user, 'C', obj)
# 观察者模式
comment_was_posted.connect(receiver=notify_comment)
