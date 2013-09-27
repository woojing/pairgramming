# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from functools import wraps

def has_username(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        request = args[0]
        if request.session.get('insta_name', '') == '':
            if request.user.is_anonymous():
                if request.POST.get('username'):
                    request.session['insta_name'] = request.POST.get('username')
                else:
                    return render_to_response('pair_session/landing.html',
                        context_instance=RequestContext(request))
            else:
                request.session['insta_name'] = request.user.username
        return func(*args, **kwargs)
    return wrapped