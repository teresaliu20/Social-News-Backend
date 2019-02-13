from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    bio = models.CharField(_("Bio of User"), max_length=280, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


class FeedSubscription(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
    rss_link = models.CharField(blank=True, max_length=255)


class Following(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, related_name="friendship_creator_set", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="friend_following_set", on_delete=models.CASCADE)


class Bookmark(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(blank=True, max_length=255)
