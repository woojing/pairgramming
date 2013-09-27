# -*- coding: utf-8 -*-
# Create your views here.
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
