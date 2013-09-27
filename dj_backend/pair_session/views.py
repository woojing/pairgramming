# -*- coding: utf-8 -*-
# Create your views here.
from subprocess import Popen, PIPE
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.http import urlencode
from django.template import RequestContext
from django.contrib.auth import logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from .models import PairRoom
import decorators

@decorators.has_username
def index(request):
    if request.POST.get('room_name', None):
        room_name = request.POST.get('room_name')
        language = request.POST.get('language')
        try:
            pm = PairRoom.objects.get(room_name=room_name)
        except PairRoom.DoesNotExist:
            pm = PairRoom(room_name=room_name, language=language)
            pm.save()
        param = urlencode({'id': room_name})
        return HttpResponseRedirect('/pair_session/?' + param)
    if request.GET.get('id',None) is None:
        return render_to_response('pair_session/landing.html',
            context_instance=RequestContext(request))
    else:
        room_name = request.GET.get('id')
        pm = PairRoom.objects.get(room_name=room_name) 
        return render_to_response('pair_session/session.html',
            {'pm': pm},
            context_instance = RequestContext(request))

@csrf_exempt
def run_code(request):
    code = request.POST.get('code')
    language = request.POST.get('language')
    result = ''
    proc = None
    if language == "python":
        proc = Popen(['python', '-c', code], stdout=PIPE, stderr=PIPE)
    elif language == "javascript":
        proc = Popen(['node', '-e', code], stdout=PIPE, stderr=PIPE)
    elif language == "ruby":
        proc = Popen(['ruby', '-e', code], stdout=PIPE, stderr=PIPE)
    result, error = proc.communicate()
    if error != '':
        result += "\nerror:%s" % error
    return HttpResponse(result, content_type="text/plain")

def logout(request):
    session = request.session
    if session.get('insta_name', None):
        del session['insta_name']

    if request.user.is_authenticated():
        django_logout(request)

    return HttpResponseRedirect('/pair_session/')
