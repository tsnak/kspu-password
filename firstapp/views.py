# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import re
from base64 import b16encode, b64decode

import ldap
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from firstapp.changepasswordfunction import change_password_function
from firstapp.getfunctions import get_cn, connect_to_ldap
from firstapp.models import Person, Admin,RegistrationAdmin

ADMIN_PASSWORD = "admin"


def add_admin(request):
    if request.session['username'] == 'admin':
        if request.method == "POST":
            try:
                admin = Admin()
                admin.fullname = get_cn(request, request.POST.get("username"))
                admin.username = request.POST.get("username").lower()
                admin.right = request.POST.get("right")
                admin.save()
            except IntegrityError:
                return render(request, "error.html", {"error": "Integrity Error"})
        return HttpResponseRedirect("/")


def edit_admin(request, user_id):
    if request.session['username'] == 'admin':
        try:
            admin = Admin.objects.get(id=user_id)
            if request.method == "POST":
                admin.username = request.POST.get("username").lower()
                admin.fullname = get_cn(request, request.POST.get("username"))
                admin.right = request.POST.get("right")
                try:
                    admin.save()
                except IntegrityError:
                    return render(request, "error.html", {"error": "Integrity Error"})
                return HttpResponseRedirect("/")
            else:
                return render(request, "admin/edit_admin.html", {"person": admin})
        except Admin.DoesNotExist:
            return render(request, "error.html", {"error": "Admin doesn't exist"})


def delete_admin(request, user_id):
    if request.session['username'] == 'admin':
        try:
            admin = Admin.objects.get(id=user_id)
            admin.delete()
            return HttpResponseRedirect("/")
        except Admin.DoesNotExist:
            return render(request, "error.html", {"error": "Admin doesn't exist"})


def index(request):
    if 'username' in request.session:
        username = request.session['username']
        if username == 'admin':
            people = Admin.objects.all()
            return render(request, 'admin/super_admin.html', {"people": people})
        try:
            changer = Admin.objects.filter(username=username)
            try:
                registration_admin = RegistrationAdmin.objects.filter(username=username)
                return render(request, 'main_menu.html', {"username": username, "changer": changer, "regAdmin": registration_admin})
            except RegistrationAdmin.DoesNotExist:
                return render(request, 'main_menu.html', {"username": username, "changer": changer})
        except Admin.DoesNotExist:
            try:
                registration_admin = RegistrationAdmin.objects.filter(username=username)
                return render(request, 'main_menu.html', {"username": username, "regAdmin": registration_admin})
            except RegistrationAdmin.DoesNotExist:
                return render(request, 'main_menu.html', {"username": username})
    else:
        return render(request, 'login.html')


def login(request):
    if (request.POST.get("uid") == "admin") & (request.POST.get("password") == ADMIN_PASSWORD):
        people = Admin.objects.all()
        request.session['username'] = request.POST.get("uid")
        return render(request, "admin/super_admin.html", {"people": people})
    ad = connect_to_ldap(request)
    if 'username' in request.session:
        if request.session['username'] == 'admin':
            people = Admin.objects.all()
            return render(request, "admin/super_admin.html", {"people": people})
        username = request.session['username']
        try:
            changer = Admin.objects.filter(username=username)
            return render(request, 'main_menu.html', {"changer": changer})
        except Admin.DoesNotExist:
            return render(request, 'main_menu.html')
    if request.method == "POST":
        username = request.POST.get("uid").lower()
        results = ad.search("dc=kspu,dc=ru", ldap.SCOPE_SUBTREE, 'uid=' + username)
        while ad:
            result_type, result_data = ad.result(results, 0)
            if result_data:
                if ((username == result_data[0][1]['uid'][0].decode("utf-8")) & (
                        (request.POST.get("password") == result_data[0][1]['userPassword'][0].decode()))):
                    request.session['username'] = username
                    ad.unbind()
                    index(request)
                try:
                    if ((username == result_data[0][1]['uid'][0].decode("utf-8")) &
                            (hashlib.md5(request.POST.get("password").encode("utf")).hexdigest()
                             == b16encode(b64decode(
                                        result_data[0][1]['userPassword'][0].decode("utf-8").strip('{MD5}').encode(
                                            "utf-8"))).lower().decode("utf-8"))):
                        request.session['username'] = username
                        ad.unbind()
                        index(request)
                except:
                    return HttpResponseRedirect("/")

            else:
                break
    ad.unbind()
    return HttpResponseRedirect("/")


def logout(request):
    if 'username' in request.session:
        del request.session['username']
    return render(request, "login.html")


def go_to_email(request):
    if 'username' not in request.session:
        return HttpResponseRedirect("/")
    try:
        user = Person.objects.get(username=request.session['username'])
        return render(request, "change_email.html", {"email": user.email})
    except Person.DoesNotExist:
        return render(request, "change_email.html", {"email": "Отсутствует"})


def change_password(request):
    if 'username' not in request.session:
        return HttpResponseRedirect("/")
    ad = connect_to_ldap(request)
    if request.method == "POST":
        results = ad.search("dc=kspu,dc=ru", ldap.SCOPE_SUBTREE, 'uid=' + request.session['username'])
        while ad:
            result_type, result_data = ad.result(results, 0)
            if result_data:
                if ((result_data[0][1]['uid'][0].decode() == request.session['username']) & (
                        request.POST.get("password") == result_data[0][1]['userPassword'][0].decode())):
                    if request.POST.get("new_password") == request.POST.get("repeat_new_password"):
                        if re.findall("(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[а-яА-Я]).{6,20}$",
                                      request.POST.get("new_password")):
                            message = change_password_function(request, request.session["username"],
                                                               request.POST.get("new_password"))
                            if message == 0:
                                return HttpResponseRedirect("/")
                            else:
                                return render(request, "change_password.html",
                                              {"message": message})
                        else:
                            return render(request, "change_password.html",
                                          {
                                              "message": "Введённый новый пароль не подходит по требованиям (6-20 символов, как минимум одна цифра, одна большая и одна маленькая буква)"})
                    else:
                        return render(request, "change_password.html",
                                      {"message": "Введённый новый пароль не совпадает"})
                try:
                    if (hashlib.md5(request.POST.get("password").encode("utf")).hexdigest()
                            == b16encode(b64decode(
                                result_data[0][1]['userPassword'][0].decode("utf-8").strip('{MD5}').encode(
                                    "utf-8"))).lower().decode("utf-8")):
                        if request.POST.get("new_password") == request.POST.get("repeat_new_password"):
                            if re.findall("(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[а-яА-Я]).{6,20}$",
                                          request.POST.get("new_password")):
                                message = change_password_function(request, request.session["username"],
                                                                   request.POST.get("new_password"))
                                if message == 0:
                                    return HttpResponseRedirect("/")
                                else:
                                    return render(request, "change_password.html",
                                                  {"message": message})
                            else:
                                return render(request, "change_password.html",
                                              {
                                                  "message": "Введённый новый пароль не подходит по требованиям (6-20 символов, как минимум одна цифра, одна большая и одна маленькая буква)"})
                        else:
                            return render(request, "change_password.html",
                                          {"message": "Введённый новый пароль не совпадает"})
                except:
                    return render(request, "change_password.html", {"message": "Неверно введён предыдущий пароль"})
                else:
                    return render(request, "change_password.html", {"message": "Неверно введён предыдущий пароль"})
            else:
                break
    ad.unbind()
    return render(request, "change_password.html")


def email(request):
    try:
        user = Person.objects.get(username=request.session['username'])

        if request.method == "POST":
            user.username = request.session['username']
            user.email = request.POST.get("email")
            user.save()
        return HttpResponseRedirect("/")
    except Person.DoesNotExist:
        if request.method == "POST":
            user = Person()
            user.username = request.session['username']
            user.email = request.POST.get("email")
            user.save()
        return HttpResponseRedirect("/")


def students_view(request):
    if 'username' not in request.session:
        return HttpResponseRedirect("/")
    if request.method == 'POST':
        list_of_uid = students_array(request, 'uid=*')
        list_of_uid.sort()
        return render(request, "students_list.html", {'students': list_of_uid})
    else:
        return render(request, "students_list.html")


def students_filter(request):
    if request.method == 'GET':
        phone = request.GET.get('phone')
        phone = phone.replace('_', ' ')
        phone = phone.replace('_', ' ')
        queryset = students_array(request, 'uid=' + '*' + phone + '*') + students_array(request,                                                                                        'cn=' + '*' + phone + '*')
        response = render(
            request,
            'array_of_students.html',
            {'students': queryset}
        )
        return response


def search_for_students(request, ad, results, list_of_uid):
    while ad:
        try:
            result_type, result_data = ad.result(results, 0)
        except ldap.NO_SUCH_OBJECT:
            return render(request, "error.html", {"error": "Неверный путь в настройках"})  # неверный путь
        except ldap.INVALID_DN_SYNTAX:
            return render(request, "error.html", {"error": "Неверный DN"})  # неверный DN
        if result_data:
            try:
                list_of_uid.append([result_data[0][1]['uid'][0].decode(), result_data[0][1]['cn'][0].decode()])
            except:
                continue
        else:
            break


def students_array(request, uid):
    ad = connect_to_ldap(request)
    admin = Admin.objects.filter(username=request.session['username'])
    list_of_uid = []
    for admin in admin:
        results = ad.search(admin.right, ldap.SCOPE_SUBTREE, uid)
        search_for_students(request, ad, results, list_of_uid)
        list_of_uid.sort()
    return list_of_uid


def change_student_password(request, username):
    if 'username' not in request.session:
        return HttpResponseRedirect("/")
    if request.method == "POST":
        ad = connect_to_ldap(request)
        try:
            admin = Admin.objects.filter(username=request.session['username'])
        except Admin.DoesNotExist:
            return render(request, "error.html", {"error": "Admin doesn't exist"})
        # @TODO Переделать, или может и не стоит, но admin.right на нескольких ветках не работает
        results = ad.search("dc=kspu,dc=ru", ldap.SCOPE_SUBTREE, 'uid=' + username)
        while ad:
            result_type, result_data = ad.result(results, 0)
            if result_data:
                message = change_password_function(request, username, request.POST.get("new_password"))
                if message == 0:
                    return HttpResponseRedirect("/students_view")
                else:
                    return render(request, "change_student_password.html", {"message": message})
            else:
                break
        ad.unbind()
        return HttpResponseRedirect("/students_view")
    else:
        return render(request, "change_student_password.html")
