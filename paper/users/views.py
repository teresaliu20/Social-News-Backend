from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from rest_framework.views import APIView
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from rest_framework.response import Response
from .models import Bookmark, FeedSubscription, Following
from .serializers import BookmarkSerializer, UserSerializer, FeedSubscriptionSerializer, FollowingSerializer
from django.core import serializers
import json
from pprint import pprint
from django.core.serializers.json import DjangoJSONEncoder

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserListView(LoginRequiredMixin, ListView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_list_view = UserListView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()

# Returns all bookmarks in database
class BookmarksListView(APIView):
    def get(self, request, format=None):
        bookmarks = Bookmark.objects.all()
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

bookmarks_list_view = BookmarksListView.as_view()

# Returns all users in database
class UsersListView(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

users_list_view = UsersListView.as_view()

# Returns all bookmarks of a specific user
class UserBookmarksView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        bookmarks = user.bookmark_set.all()
        data = serializers.serialize('json', list(bookmarks), fields=('created', 'creator','link'))
        return Response(json.loads(data))

    def post(self, request, pk, format=None):
        user = self.get_object(pk)
        bLink = self.request.data.get('link')

        if user and bLink:
            b = Bookmark(link=bLink, creator=user)
            b.save()
            serializer = BookmarkSerializer(b)
            return Response(serializer.data)
        else:
            return Response('Error: Unable to find either user or POST link data', status=HTTP_400_BAD_REQUEST)

user_bookmarks_view = UserBookmarksView.as_view()

# Returns all rss links that user is subscribed to
class UserFeedView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        feed = user.feedsubscription_set.all()
        data = serializers.serialize('json', list(feed), fields=('created', 'subscriber','rss_link'))
        return Response(json.loads(data))

    def post(self, request, pk, format=None):
        user = self.get_object(pk)
        fLink = self.request.data.get('link')

        if user and fLink:
            subscription = FeedSubscription(subscriber=user, rss_link=fLink)
            subscription.save()
            serializer = FeedSubscriptionSerializer(subscription)
            return Response(serializer.data)
        else:
            return Response('Error: Unable to find either user or POST link data', status=HTTP_400_BAD_REQUEST)

users_feed_view = UserFeedView.as_view()

# Returns all the people a specific user is following
class UserFollowingView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        following = user.friendship_creator_set.all()
        data = serializers.serialize('json', list(following), fields=('created', 'creator','following'))
        return Response(json.loads(data))

    def post(self, request, pk, format=None):
        user = self.get_object(pk)
        following_id = self.request.data.get('user_id')
        print(self.request.data.get('user_id'))

        if user and following_id:
            followingUser = User.objects.get(pk=following_id)
            f = Following(creator=user, following=followingUser)
            f.save()
            serializer = FollowingSerializer(f)
            return Response(serializer.data)
        else:
            return Response('Error: Unable to find either user or POST link data', status=HTTP_400_BAD_REQUEST)

users_following_view = UserFollowingView.as_view()

# Returns the social feed of a user: all bookmarks of people you are following
class UserSocialFeedView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        following = user.friendship_creator_set.all()
        data = json.loads(serializers.serialize('json', list(following), fields=('created', 'creator','following')))

        socialFeed = []

        for u in data:
            followingUser = User.objects.get(pk=u["fields"]["following"])
            bookmarks = followingUser.bookmark_set.all()
            socialFeed += json.loads(serializers.serialize('json', list(bookmarks), fields=('created', 'creator','link')))

        return Response(socialFeed)

users_social_feed_view = UserSocialFeedView.as_view()
