from rest_framework import serializers
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from .models import User, FeedSubscription, Following, Bookmark

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ('username', )
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }


class FeedSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedSubscription
        fields = '__all__'


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = '__all__'
