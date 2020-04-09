from os import path
from django.apps import AppConfig

VERBOSE_APP_NAME = "scheduler"


def get_current_app_name(file):
    return path.dirname(file).replace('\\', '/').split('/')[-1]


class AppVerboseNameConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = '任务调度'


default_app_config = get_current_app_name(__file__) + '.__init__.AppVerboseNameConfig'
