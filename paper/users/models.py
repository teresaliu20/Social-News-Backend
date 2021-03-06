import sys
from io import BytesIO
import base64
import PIL
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.files.uploadedfile import InMemoryUploadedFile
from .enums import Relationship, CollectionPermission

class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    bio = models.CharField(_("Bio of User"), max_length=280, blank=True, null=True)
    image = models.ImageField(upload_to='profile_image', blank=True, null=True)
    linksProposed = models.IntegerField(default=0)
    linksAccepted = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class Following(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, related_name="friendship_creator_set", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="friend_following_set", on_delete=models.CASCADE)


class Collection(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=255)
    description = models.CharField(blank=True, max_length=3000)
    permission = models.CharField(blank=True, max_length=30, choices=[(permission.name, permission.value) for permission in CollectionPermission])

    def __str__(self):  # what will be displayed in the admin
        return "Name: " + self.name + ", Id: " + str(self.id)


class Topic(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    name = models.CharField(blank=True, max_length=255)
    collection = models.ForeignKey(Collection, blank=True, null=True, related_name="tag_set", on_delete=models.CASCADE)


class Link(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(blank=True, max_length=255)
    collection = models.ForeignKey(Collection, blank=True, null=True, related_name="collection_set", on_delete=models.CASCADE)
    description = models.CharField(blank=True, max_length=3000)
    inReadingList = models.BooleanField(default=False)


class CollectionRelationship(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    start = models.ForeignKey(Collection, related_name="origin", blank=True, null=True, on_delete=models.CASCADE)
    end = models.ForeignKey(Collection, related_name="endpoint", blank=True, null=True, on_delete=models.CASCADE)
    relationship = models.CharField(blank=True, max_length=30, choices=[(tag.name, tag.value) for tag in Relationship])
    approved = models.BooleanField(default=False)
