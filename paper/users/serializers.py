from rest_framework import serializers
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from .models import User, Following, Link, Collection, CollectionRelationship, Topic

class UserSerializer(serializers.ModelSerializer):

    # image = ImageSerializer()

    class Meta:
        model = User
        # exclude = ('username', )
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

class UserPartSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'name', 'image')
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
    author = UserPartSerializer()
    class Meta:
        model = Collection
        fields = '__all__'


class CollectionRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRelationship
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
