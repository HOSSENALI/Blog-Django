"""djangoblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [

    path('', views.index.as_view(), name="index"),
    path('author/<name>', views.getauthor.as_view(), name="author"),
    path('single/<int:id>', views.getsingle, name="single_post"),
    path('topic/<name>', views.getTopic, name="topic"),
    path('login', views.getLogin, name="login"),
    path('logout', views.getlogout, name="logout"),
    path('create', views.getcreate, name="create"),
    path('profile', views.getProfile, name="profile"),
    path('update/<int:pid>', views.getUpdate, name="update"),
    path('delete/<int:pid>', views.getDelete, name="delete"),
    path('register', views.getRegister, name="register"),
    path('category', views.getCategory, name="category"),
    path('createCategory', views.createCategory, name="createCategory"),

    # account confirmations
    path('activate/<uid>/<token>', views.activate, name="activate"),

    path('pdf/<int:id>', views.pdf, name="pdf"),

    # Json and Xml
    path('json', views.getJson, name="json"),
    path('xml', views.getXml, name="xml"),
]
