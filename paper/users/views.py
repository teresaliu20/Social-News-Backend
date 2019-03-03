from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from rest_framework.response import Response
from .models import Link, Following, Collection, CollectionRelationship
from .serializers import LinkSerializer, UserSerializer, FollowingSerializer, CollectionSerializer, CollectionRelationshipSerializer
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json

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

class UserInformationView(APIView):
    def get(self, request, pk, format=None):
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

user_information_view = UserInformationView.as_view()

# Returns all bookmarks in database
class LinksListView(APIView):
    def get(self, request, format=None):
        bookmarks = Link.objects.all()
        serializer = LinkSerializer(bookmarks, many=True)
        return Response(serializer.data)

bookmarks_list_view = LinksListView.as_view()

# Returns all users in database
class UsersListView(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

users_list_view = UsersListView.as_view()

# Returns all bookmarks of a specific user
class UserLinksView(APIView):
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
            b = Link(url=bLink, creator=user)
            b.save()
            serializer = LinkSerializer(b)
            return Response(serializer.data)
        else:
            return Response('Error: Unable to find either user or POST link data', status=HTTP_400_BAD_REQUEST)

user_bookmarks_view = UserLinksView.as_view()

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

# Returns the collections that a specific user has made
class UserCollectionsView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        collections = Collection.objects.filter(owner=user)
        print(collections)
        data = json.loads(serializers.serialize('json', list(collections), fields=('created', 'owner','name')))

        return Response(data)

users_collections_view = UserCollectionsView.as_view()

# Returns collection information based on id
class CollectionView(APIView):
    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        collection = self.get_object(pk)
        cs = CollectionSerializer(collection)
        links = Link.objects.filter(collection=collection)

        data = {}
        data["collectionInfo"] = cs.data
        data["Links"] = json.loads(serializers.serialize('json', list(links), fields=('created', 'creator','url')))

        return Response(data)

    def post(self, request, format=None):
        name = request.data['name']
        owner_id = request.data['user_id']
        description = request.data['description']

        urls = request.data['links']

        data = {}

        owner = User.objects.get(pk=owner_id)

        collection = Collection(owner=owner, name=name, description=description)
        collection.save()

        data["collectionInfo"] = CollectionSerializer(collection).data
        print(data["collectionInfo"])
        links = []

        if urls:
            for url in urls:
                tempLink = Link(creator=owner, url=url, collection=collection)
                print("hi" + url)
                tempLink.save()
                links.append(LinkSerializer(tempLink).data)

        data["links"] = links

        print(data)

        return Response(data)

    def delete(self, request, format=None):
        collection_id = request.data['collection_id']

        collection = Collection.objects.get(pk=collection_id).delete()

        return Response(status=HTTP_200_OK)

collection_view = CollectionView.as_view()

# Returns all collections that are connected to the one requested based on id
class CollectionConnectedView(APIView):
    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        collection = self.get_object(pk)

        connections = CollectionRelationship.objects.filter(start=collection)

        data = []
        for c in connections:
            currConnection = c.end

            cs = CollectionSerializer(currConnection)
            links = Link.objects.filter(collection=currConnection)

            subCollection = {}
            subCollection["collectionInfo"] = cs.data
            subCollection["links"] = json.loads(serializers.serialize('json', list(links), data=('created', 'creator','url')))
            subCollection["approved"] = c.approved
            subCollection["relationship"] = c.relationship

            data.append(subCollection)

        return Response(data)

collection_connected_view = CollectionConnectedView.as_view()

# Returns all collections that are connected to the one requested based on id
class CollectionRelationshipView(APIView):
    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        collection_id = request.data['collectionFrom']
        collection_id2 = request.data['collectionTo']
        relation = request.data['relationship']

        collectionFrom = self.get_object(collection_id)
        collectionTo = self.get_object(collection_id2)

        cr = CollectionRelationship(start=collectionFrom, end=collectionTo, relationship=relation, approved=False)

        cr.save()

        return Response(CollectionRelationshipSerializer(cr).data, status=HTTP_200_OK)

    def delete(self, request, format=None):
        relationship_id = request.data['relationship_id']

        collectionRelationship = CollectionRelationship.objects.get(pk=relationship_id).delete()

        return Response(status=HTTP_200_OK)


collection_relationship_view = CollectionRelationshipView.as_view()


class Login(APIView):
    """
    POST: Log in a user based on the username and password submitted
    """
    def post(self, request, format=None):
        error_resp = Response({'detail': 'Failed to login user'}, status=400)
        serializer_context = {
            'request': request,
        }
        try:
            username = request.data['username']
            password = request.data['password']
            auth_user = authenticate(request, username=username, password=password)
        except Exception as e:
            print(e.detail)
            return error_resp

        if auth_user is not None:
            try:
                login(request, auth_user)
                serialized_user = UserSerializer(auth_user, context=serializer_context)
                return Response(serialized_user.data, status=200)
            except Exception as e:
                print(e.detail)
                return error_resp
        else:
            return error_resp

login_view = Login.as_view()


class Logout(APIView):
    """
    POST: Log out a user
    """
    def post(self, request, format=None):
        try:
            logout(request)
            return Response({'detail': 'Logout successful'})
        except Exception:
            return Response({'detail': 'Server error occured on logout'})

logout_view = Logout.as_view()


class SignUp(APIView):
    def post(self, request, format=None):
        try:
            username = request.data['username']
            email = request.data['email']
            password = request.data['password']

            user = User.objects.create_user(username, email, password)

            user.first_name = request.data['firstname']
            user.last_name = request.data['lastname']

            user.save()

            serialized_user = UserSerializer(user)

            return Response(serialized_user.data)
        except Exception as e:
            print (e.message)
            return Response({'detail': 'Server error occured on signup'})

signup_view = SignUp.as_view()
