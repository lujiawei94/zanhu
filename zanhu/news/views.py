from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from django.template.loader import render_to_string
from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

from zanhu.news.models import News
from zanhu.helpers import ajax_required, AuthorRequireMixin


class NewsListView(LoginRequiredMixin, ListView):
    model = News
    # queryset = News.objects.all()  # 默认模型类的全部对象，可以做简单过滤，更常用的通过get_queryset实现动态过滤
    paginate_by = 20  # 默认url中的？page=
    # page_kwarg = 'p'  #修改url中的显示
    # context_object_name = 'news_list'  # 定义qureyset查询集在template中的变量名，默认是模型类名_list或object_list
    template_name = 'news/news_list.html'  # 默认'模型类名_list.html'
    ordering = 'created_at'  # ('x', 'y', )

    def get_queryset(self):
        """实现动态过滤"""
        return News.objects.filter(reply=False).select_related('user', 'parent').prefetch_related('liked')

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     """除了model定义的模型类中的数据(或已被动态过滤的数据)，添加额外的上下文"""
    #     context = super().get_context_data()
    #     context['views'] = 100
    #     return context  # 除了过滤后的数据，还包含了views


class NewsDeleteView(LoginRequiredMixin, AuthorRequireMixin, DeleteView):
    model = News
    template_name = 'news/news_confirm_delete.html'
    # slug_url_kwarg = 'slug'  # 通过url传入要删除的对象主键id，默认为slug
    # pk_url_kwarg = 'pk'  # 通过url传入要删除的对象主键id，默认为pk
    success_url = reverse_lazy('news:list')  # 删除后跳转的路径 reverse_lazy(在项目URLConf未加载前使用)


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    """发送动态，ajax post请求"""
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string('news/news_single.html', {'news': posted, 'request': request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest('内容不能为空！')


@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    """点赞， AJAX POST 请求"""
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    news.switch_like(request.user)
    return JsonResponse({'likes': news.count_likers()})


@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    """获取动态评论，AJAX GET请求"""
    news_id = request.GET['news']
    news = News.objects.select_related('user').get(pk=news_id)
    news_html = render_to_string('news/news_single.html', {'news': news})  # 没有评论时
    thread_html = render_to_string('news/news_thread.html', {'thread': news.get_thread()})
    return JsonResponse({
        'uuid': news_id,
        'news': news_html,
        'thread': thread_html
    })


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_comment(request):
    """评论，AJAX POST请求"""
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    return HttpResponseBadRequest('评论不能为空')

@login_required
@ajax_required
@require_http_methods(['POST'])
def update_interactions(request):
    data_point = request.POST['id_value']
    news = News.objects.get(pk=data_point)
    return JsonResponse({'likes': news.count_likers,
                         'comments': news.comment_count()})

