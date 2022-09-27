"""votewebG URL Configuration

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
from django import urls

from django.contrib import admin
from django.urls import path,include
from polls import views,autocomplete
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('',views.frontdex),
  path('index',views.index, name='index'),
    path('deletevote/<str:election_id>/', views.deletevote, name='deletevote'),
    path('editvote/<str:election_id>/', views.editvote,name='editvote'),
    path('managevote',views.managevote, name="managevote"),
    path('managepoll', views.managepoll, name='managepoll'),
    path('polledit/<str:poll_id>/', views.polledit,name='polledit'),
    path('polldelete/<str:poll_id>/', views.polldelete, name='polldelete'),
    path('manageadmin', views.manageadmin, name='manageadmin'),
    path('edituser/<str:user_id>/', views.edituser,name='edituser'),
    path('report', views.report),
    path('register',views.register, name='register'),
    path('loginform',views.loginform, name='loginform'),
    path('logoutUser',views.logoutUser, name='logoutUser'),
    path('',include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
#front end
    path('frontdex', views.frontdex, name='frontdex'),
    path('createvote', views.createvote, name='createvote'),
    path('vote', views.vote, name='vote'),
    path('createpoll', views.PollView.as_view(), name='createpoll'),
    path('editpoll/<int:id>/', views.PollView.as_view(), name='editpoll'),
    path('deletepoll/<int:id>/', views.deletepoll, name='deletepoll'),
    path('letvote/<str:poll_id>/', views.letvote, name='letvote'),
    path('letpoll/<str:poll_id>/', views.letpoll, name='letpoll'),
    path('pollresult/<str:poll_id>/', views.pollresult, name='pollresult'),
    path('createelect', views.ElectView.as_view(), name='createelect'),
    path('editelect/<int:id>/', views.ElectView.as_view(), name='editelect'),
    path('letelect/<str:election_id>/', views.letelect, name='letelect'),
    path('electresult/<str:election_id>/', views.electresult, name='electresult'),
    path('deleteelect/<int:id>/', views.deleteelect, name='deleteelect'),    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
