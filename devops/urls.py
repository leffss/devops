"""devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from server.views import index

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
    
    path('admin/', admin.site.urls),
    
    path('', index),
    
    path('server/', include('server.urls', namespace='server')),
    path('api/server/', include('server.urls_api', namespace='server_api')),
    
    path('user/', include('user.urls', namespace='user')),
    path('api/user/', include('user.urls_api', namespace='user_api')),
    
    path('webssh/', include('webssh.urls', namespace='webssh')),
    path('api/webssh/', include('webssh.urls_api', namespace='webssh_api')),
    
    path('webtelnet/', include('webtelnet.urls', namespace='webtelnet')),
    
]
