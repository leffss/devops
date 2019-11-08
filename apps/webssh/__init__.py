from os import path
from django.apps import AppConfig

VERBOSE_APP_NAME = "webssh"


def get_current_app_name(file):
    return path.dirname(file).replace('\\', '/').split('/')[-1]


class AppVerboseNameConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name = 'webssh终端'


default_app_config = get_current_app_name(__file__) + '.__init__.AppVerboseNameConfig'
