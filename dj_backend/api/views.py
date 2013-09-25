# -*- coding: utf-8 -*-
# Create your views here.
from allauth.socialaccount.models import SocialAccount
from rest_framework import viewsets
from .serializers import SocialAccountSerializer


class SocialAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = SocialAccount.objects.all()
    serializer_class = SocialAccountSerializer
