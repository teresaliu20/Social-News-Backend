from rest_framework import serializers
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from .models import User, FeedSubscription, Following, Link, Collection

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ('username', )
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
        

class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'
