from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArticlesConfig(AppConfig):
    name = 'zanhu.articles'
    verbose_name = _('文章')
