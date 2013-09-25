# -*- coding: utf-8 -*-
from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers

class SocialAccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar_url = serializers.URLField(source='get_avatar_url', read_only=True)
    class Meta:
        model = SocialAccount
        fields = ('username', 'avatar_url')
