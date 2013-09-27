# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

def create_anon_user(request):
    session = request.session
    session['username'] = request.POST.get('username')
