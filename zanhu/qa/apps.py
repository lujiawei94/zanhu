from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QaConfig(AppConfig):
    name = 'zanhu.qa'
    verbose_name = _('问答')
