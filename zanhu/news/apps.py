from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class NewsConfig(AppConfig):
    name = 'zanhu.news'
    verbose_name = _('赞乎')
