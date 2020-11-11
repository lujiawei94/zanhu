from functools import wraps
from django.http.response import HttpResponseBadRequest
from django.views.generic import View
from django.core.exceptions import PermissionDenied


def ajax_required(f):
    """验证是否为ajax请求"""
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("不是ajax请求")
        return f(request, *args, **kwargs)
    return wrapper


class AuthorRequireMixin(View):
    """验证是否为原作者，用于删除状态或文章编辑"""
    def dispatch(self, request, *args, **kwargs):
       # 状态和文章实例有user属性，需要与登录user一致
        if self.get_object().user.username != request.user.username:
            return PermissionDenied
        return super().dispatch(request, *args, **kwargs)
