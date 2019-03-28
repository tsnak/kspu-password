"""NewProject URL Configuration

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
from django.conf.urls import url
from django.urls import path
from firstapp import views, registration, accept_user, registration_admin, activation, password_recovery

urlpatterns = [
    path('', views.index),
    path('add_admin', views.add_admin),
    path('registration_admin', registration_admin.add_admin),
    path('registration_admin/delete/<int:id>', registration_admin.delete_admin),
    path('login', views.login),
    path('change_password', views.change_password),
    path('logout', views.logout),
    path('go_to_email', views.go_to_email),
    path('email', views.email),
    path('forgot_password', password_recovery.forgot_password),
    path('registration/', registration.registration),
    path('activation/', activation.activation),
    path('activation/notes/', activation.notes),
    path('accept_user', accept_user.users_to_accept_list),
    path('add_user/<int:id>/', accept_user.add_user),
    path('delete_user/<int:id>/', accept_user.delete_user),
    path('registration/<str:path>', registration.registration),
    path('edit_admin/<int:user_id>/', views.edit_admin),
    path('delete_admin/<int:user_id>/', views.delete_admin),
    path('students_view/', views.students_view),
    path('students_view/change_student_password/<str:username>/', views.change_student_password),
    path('password_recovery/<str:secret_key>/', password_recovery.password_recovery),
    url(r'^array_of_students/', views.students_filter, name='array_of_students'),
]
