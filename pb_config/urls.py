"""PBcompany URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('bookings.urls', namespace='bookings')),
    url(r'users/', include('users.urls', namespace='users')),

    url(r'^password_reset_complete/$', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
        name='password_reset_complete'),
    # ^^ This page is displayed after a user succesfully resets
    # their password. The reason it is here is because I was not
    # able to find a way for it to route correctly to the users
    # url app. It works right now if it is in both url files.
    # Removing either of them will result in a NoReverseMatch error
    # removing this one will result in a request method POST error
    # removing user/urls will result in a request method Get error
    # will figure this out another time. 
    ]

