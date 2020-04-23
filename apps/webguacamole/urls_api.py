from django.urls import path
from . import views_api


app_name = "webguacamole"
urlpatterns = [
    path('session/upload/', views_api.session_upload, name='session_upload'),
]
