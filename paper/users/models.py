from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    bio = models.CharField(_("Bio of User"), max_length=280, blank=True, null=True)
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
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=255)
    description = models.CharField(blank=True, max_length=500)

    def __str__(self):  # what will be displayed in the admin
        return "Name: " + self.name + ", Id: " + str(self.id)

class Link(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(blank=True, max_length=255)
    collection = models.ForeignKey(Collection, blank=True, null=True, related_name="collection_set", on_delete=models.CASCADE)
