# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='username', read_only=True)
    avatar_url = serializers.URLField(source='socialaccount_set.get.get_avatar_url', read_only=True)
    class Meta:
        model = User
        fields = ('username', 'avatar_url')
