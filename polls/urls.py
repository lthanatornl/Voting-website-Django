from django.urls import path
from django.urls.resolvers import URLPattern
from polls import views

URLPattern = [
    path('',views.index)
]

