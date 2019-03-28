import ldap
from django.shortcuts import render


def get_cn(request, username):
    ad = connect_to_ldap(request)
    results = ad.search("dc=kspu,dc=ru", ldap.SCOPE_SUBTREE, 'uid=' + username)
    while ad:
        result_type, result_data = ad.result(results, 0)
        if result_data:
            ad.unbind()
            return result_data[0][1]['cn'][0].decode()
        else:
            break


def connect_to_ldap(request):
    try:
        ad = ldap.initialize("ldap://ldap.kspu.ru:389", bytes_mode=False)
        ad.simple_bind_s("cn=admin,dc=kspu,dc=ru", "help")
        return ad
    except ldap.CONNECT_ERROR:
        return render(request, "error.html", {"error": "LDAP connection error"})