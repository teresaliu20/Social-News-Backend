import json
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse, Http404
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.response import Response
from .models import Link, Following, Collection, CollectionRelationship, Topic
from .serializers import LinkSerializer, UserSerializer, FollowingSerializer, CollectionSerializer, CollectionRelationshipSerializer, TopicSerializer

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
    def post(self, request, format=None):
        user_id = request.data["user_id"]
        isLoggedInUser = request.data["isLoggedInUser"]

        user = User.objects.get(pk=user_id)
        serializer = UserSerializer(user)
        data = serializer.data

        if not isLoggedInUser:
            data.pop('email', None)
            data.pop('is_superuser', None)
            data.pop('groups', None)
            data.pop('user_permissions', None)
            data.pop('is_staff', None)

        return Response(data)

user_information_view = UserInformationView.as_view()

# Edit user profile
class EditUserView(APIView):
    def post(self, request, format=None):
        user_id = request.data["user_id"]
        username = request.data['username']
        email = request.data['email']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        name = request.data['name']
        bio = request.data['bio']

        user = User.objects.get(pk=user_id)
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.name = name

        user.save()

        return Response(UserSerializer(user).data)

edit_user_view = EditUserView.as_view()

# Returns users in database that match a prefix search of username, first name, full name, and email
class SearchUsersView(APIView):
    def post(self, request, format=None):
        query = request.data["query"]

        username_query = Q(username__istartswith=query)
        first_name_query = Q(first_name__istartswith=query)
        name_query = Q(name__istartswith=query)
        email_query = Q(email__istartswith=query)

        search = User.objects.filter(username_query | first_name_query | name_query | email_query).values('id', 'username', 'first_name', 'last_name', 'email')

        data = list(search)

        return Response(data)

search_users_view = SearchUsersView.as_view()

# Returns collections in database that match a given name query
class SearchCollectionsView(APIView):
    def post(self, request, format=None):
        query = request.data["query"]

        search = Collection.objects.filter(name__istartswith=query).values('id', 'name', 'description')

        data = list(search)

        return Response({"collections" : data})

search_collections_view = SearchCollectionsView.as_view()

# Returns all links in user's reading list, adds new link into reading list, and deletes link from reading list
class UserReadingListView(APIView):

    def get(self, request, pk, format=None):
        user_filter = Q(owner_id=pk)
        reading_list_filter = Q(inReadingList=True)

        reading_list = Link.objects.filter(user_filter, reading_list_filter).values('id', 'created', 'owner', 'url', 'collection')

        return Response(list(reading_list))

    def post(self, request, format=None):
        user_id = request.data['user_id']
        url = request.data['url']

        owner = User.objects.get(pk=user_id)

        readingLink = Link(owner=owner, url=url, inReadingList=True)

        readingLink.save()

        return Response(LinkSerializer(readingLink).data)

    def delete(self, request, format=None):
        link_id = request.data['link_id']

        Link.objects.get(pk=link_id).delete()

        return Response(status=HTTP_200_OK)

user_reading_list_view = UserReadingListView.as_view()

# Returns all the people a specific user is following
class UserFollowingView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        following = user.friendship_creator_set.all()
        data = serializers.serialize('json', list(following), fields=('created', 'creator', 'following'))
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

        return Response('Error: Unable to find either user or POST link data', status=HTTP_400_BAD_REQUEST)

users_following_view = UserFollowingView.as_view()

# Returns the collections that a specific user has made
class UserCollectionsView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        collections = Collection.objects.filter(owner=user).values('created', 'owner', 'name', 'description', 'id')

        return Response({'collections': list(collections)})

users_collections_view = UserCollectionsView.as_view()


class TopicView(APIView):
    def get(self, request, topic_name, format=None):
        # topic_name = request.data['topic_name']
        collections = Topic.objects.filter(name__iexact=topic_name).values_list('collection', flat=True)

        cList = []
        for collection in collections:
            cList += Collection.objects.filter(pk=collection).values('created', 'owner', 'name', 'description', 'id')

        return Response({'collections': cList})

    def delete(self, request, format=None):
        topic_name = request.data['topic_name']

        Topic.objects.filter(name=topic_name).delete()

        return Response(status=HTTP_200_OK)

topic_view = TopicView.as_view()


class CreateTopicView(APIView):
    def post(self, request, format=None):
        topic_name = request.data['topic_name']
        collection_id = request.data['collection_id']

        collection = Collection.objects.get(pk=collection_id)

        name_filter = Q(name=topic_name)
        collection_filter = Q(collection=collection)

        existSet = Topic.objects.filter(name_filter, collection_filter)

        if not existSet:
            print("Topic {} does not exist yet. Creating...".format(topic_name))
            topic = Topic(name=topic_name, collection=collection)
            topic.save()
            return Response(status=HTTP_200_OK)

        return Response({'Error': "Topic already exists for this collection!"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

create_topic_view = CreateTopicView.as_view()


class SearchTopicsView(APIView):
    def post(self, request, format=None):
        query = request.data['query']
        return Response(searchTopic(query))

search_topics_view = SearchTopicsView.as_view()


class AllTopicsView(APIView):
    def get(self, request, format=None):
        return Response(searchTopic(""))

all_topics_view = AllTopicsView.as_view()


# Returns collection information based on id
class CollectionView(APIView):
    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404("User does not exist")

    def get(self, request, pk, format=None):
        collection = self.get_object(pk)
        cs = CollectionSerializer(collection)
        links = Link.objects.filter(collection=collection).values('created', 'owner', 'url', 'collection')
        topics = Topic.objects.filter(collection=collection).values_list('name', flat=True)

        data = {}
        data["collectionInfo"] = cs.data
        data["links"] = list(links)
        data["topics"] = list(topics)

        return Response(data)

    def post(self, request, format=None):
        name = request.data['name']
        owner_id = request.data['user_id']
        description = request.data['description']
        urls = request.data['links']
        topics = request.data['topics']

        owner = User.objects.get(pk=owner_id)

        collection = Collection(owner=owner, name=name, description=description)
        collection.save()

        data = {}
        data["collectionInfo"] = CollectionSerializer(collection).data

        links = []
        topicsRet = []
        if urls:
            for url in urls:
                tempLink = Link(owner=owner, url=url, collection=collection)
                print("hi" + url)
                tempLink.save()
                links.append(LinkSerializer(tempLink).data)

        if topics:
            for topic in topics:
                print("topic: {}".format(topic))
                tempTopic = Topic(name=topic, collection=collection)
                tempTopic.save()
                topicsRet.append(TopicSerializer(tempTopic).data)

        data["links"] = links
        data["topics"] = topicsRet

        print(data)

        return Response(data)

    def delete(self, request, format=None):
        collection_id = request.data['collection_id']

        collection = Collection.objects.get(pk=collection_id).delete()

        return Response(status=HTTP_200_OK)

collection_view = CollectionView.as_view()

# Returns collection information based on id
class EditCollectionView(APIView):
    def get_object(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        collection_id = request.data['collection_id']
        name = request.data['name']
        owner_id = request.data['user_id']
        description = request.data['description']
        urls = request.data['links']
        topics = request.data['topics']

        collection = Collection.objects.get(pk=collection_id)
        collection.name = name
        collection.description = description

        collection.save()

        data = {}
        data["collectionInfo"] = CollectionSerializer(collection).data

        owner = User.objects.get(pk=owner_id)

        # Delete all existing links from DB and re-add links to DB
        tempLink = Link.objects.filter(owner__id=owner_id, collection__id=collection_id)
        if tempLink:
            print("Deleting {} from db...".format(tempLink.values()))
            tempLink.delete()

        links = []
        # Re-add all links into DB
        for url in urls:
            print("Adding {} to db...".format(url))
            newLink = Link(owner=owner, url=url, collection=collection)
            newLink.save()
            links.append(LinkSerializer(newLink).data)

        # Delete all existing topics from DB and re-add topics to DB
        tempTopics = Topic.objects.filter(collection=collection)
        if tempTopics:
            print("Deleting {} from db...".format(tempTopics.values()))
            tempTopics.delete()
        # Re-add all topics into DB
        topicsRet = []
        for topic in topics:
            print("Adding topic {}".format(topic))
            newTopic = Topic(name=topic, collection=collection)
            newTopic.save()
            topicsRet.append(TopicSerializer(newTopic).data)

        data["links"] = links
        data["topics"] = topicsRet

        return Response(data)

edit_collection_view = EditCollectionView.as_view()

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

            subCollection = {}
            subCollection["collectionInfo"] = cs.data
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
            return error_resp

        if auth_user is not None:
            try:
                login(request, auth_user)
                serialized_user = UserSerializer(auth_user, context=serializer_context)
                return Response(serialized_user.data, status=200)
            except Exception as e:
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
            return Response({'detail': 'Server error occured on signup'})

signup_view = SignUp.as_view()

# Should move to its own file — here for now
def searchTopic(query):
    if not query:
        return Topic.objects.values_list('name', flat=True).distinct()

    return Topic.objects.filter(name__istartswith=query).values_list('name', flat=True).distinct()
