# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    # import ipdb; ipdb.set_trace()
    return render_to_response('pair_session/session.html',
        context_instance = RequestContext(request))