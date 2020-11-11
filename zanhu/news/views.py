from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from zanhu.news.models import News


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
        return News.objects.filter(reply=False)

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     """除了model定义的模型类中的数据(或已被动态过滤的数据)，添加额外的上下文"""
    #     context = super().get_context_data()
    #     context['views'] = 100
    #     return context  # 除了过滤后的数据，还包含了views


