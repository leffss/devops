from django.urls import path
from . import views_api

app_name = "server"
urlpatterns = [
    path('host/delete/', views_api.host_delete, name='host_delete'),
    path('host/update/', views_api.host_update, name='host_update'),
    # celery 使用 ansible 更新主机详细信息
    path('host/update/info/', views_api.host_update_info, name='host_update_info'),
    path('host/add/', views_api.host_add, name='host_add'),
    
    path('user/update/', views_api.user_update, name='user_update'),
    path('user/add/', views_api.user_add, name='user_add'),
    path('user/delete/', views_api.user_delete, name='user_delete'),

    path('group/update/', views_api.group_update, name='group_update'),
    path('group/delete/', views_api.group_delete, name='group_delete'),
    path('group/add/', views_api.group_add, name='group_add'),

]
