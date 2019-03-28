from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from firstapp.getfunctions import get_cn
from firstapp.models import RegistrationAdmin


def add_admin(request):
    if request.method == "GET" and request.session['username'] == 'admin':
        people = RegistrationAdmin.objects.all()
        return render(request, "admin/registration_admin.html", {"people": people})
    if request.method == "POST" and request.session['username'] == 'admin':
        try:
            admin = RegistrationAdmin()
            admin.fullname = get_cn(request, request.POST.get("username"))
            admin.username = request.POST.get("username").lower()
            admin.save()
        except IntegrityError:
            return render(request, "error.html", {"error": "Integrity Error"})
        return HttpResponseRedirect("/registration_admin")


def delete_admin(request, id):
    if request.session['username'] == 'admin':
        try:
            admin = RegistrationAdmin.objects.get(id=id)
            admin.delete()
            return HttpResponseRedirect("/registration_admin")
        except RegistrationAdmin.DoesNotExist:
            return render(request, "error.html")