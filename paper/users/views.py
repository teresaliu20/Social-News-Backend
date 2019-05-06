import json
import PIL
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse, Http404
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.utils.text import get_valid_filename
from rest_framework.views import APIView
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .models import Link, Following, Collection, CollectionRelationship, Topic
from .serializers import LinkSerializer, UserSerializer, UserPartSerializer, FollowingSerializer, CollectionSerializer, CollectionRelationshipSerializer, TopicSerializer
from .enums import Relationship, CollectionPermission


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

    def get_User(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def post(self, request, format=None):
        user_id = request.data["user_id"]
        isLoggedInUser = request.data["isLoggedInUser"]

        user = self.get_User(pk=user_id)
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

        name_query = Q(name__istartswith=query)
        public_privacy_query = Q(permission='Public')

        search = Collection.objects.filter(name_query, public_privacy_query).values('id', 'name', 'author', 'description', 'permission')

        data = list(search)

        for collection in data:
            print(collection["author"])
            collection["author"] = UserPartSerializer(User.objects.get(pk=collection["author"])).data

        return Response({"collections" : data})

search_collections_view = SearchCollectionsView.as_view()


# Returns all links in user's reading list, adds new link into reading list, and deletes link from reading list
class UserReadingListView(APIView):

    def get(self, request, pk, format=None):
        user_filter = Q(owner_id=pk)
        reading_list_filter = Q(inReadingList=True)

        reading_list = Link.objects.filter(user_filter, reading_list_filter).values('id', 'created', 'owner', 'url', 'collection', 'description')

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
    def get_User(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def get_Following(self, follower, followee):
        creator_filter = Q(creator_id=follower)
        following_filter = Q(following=followee)

        return Following.objects.filter(creator_filter, following_filter)

    def get(self, request, pk, format=None):
        user = self.get_User(pk)
        following = user.friendship_creator_set.values('following')
        following_list = list(following)

        data = []
        for single_user in following_list:
            following_id = single_user["following"]
            user_data = User.objects.filter(pk=following_id).values('id', 'username', 'first_name', 'last_name', 'name', 'image')
            collection_count = Collection.objects.filter(author=following_id).count()
            print("collection count is: {}".format(collection_count))

            serialized_user_data = list(user_data)

            print(serialized_user_data)
            serialized_user_data[0]["collection_count"] = collection_count

            data += serialized_user_data

        return Response(data)

    def post(self, request, pk, format=None):
        user = self.get_User(pk)
        following_id = request.data['following_id']

        if user and following_id:
            followingUser = User.objects.get(pk=following_id)

            if(self.get_Following(pk, following_id)):
                return Response('Error: Following already exists!', status=HTTP_400_BAD_REQUEST)

            f = Following(creator=user, following=followingUser)
            f.save()
            serializer = FollowingSerializer(f)
            return Response(serializer.data)

        return Response('Error: Unable to find either user or POST link data', status=HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        following_id = request.data['delete_id']

        self.get_Following(pk, following_id).delete()

        return Response(status=HTTP_200_OK)


users_following_view = UserFollowingView.as_view()


# Returns all the followers of a user
class UserFollowersView(APIView):
    def get_User(self, pk):
        try:
            return User.objects.filter(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def get(self, request, pk, format=None):
        user = self.get_User(pk)

        following = Following.objects.filter(following_id=pk).values()

        data = []
        for relationship in following:
            follower = self.get_User(relationship['creator_id']).values('id', 'username', 'first_name', 'last_name', 'name', 'image')

            collection_count = Collection.objects.filter(author=relationship['creator_id']).count()

            serialized_user_data = list(follower)
            serialized_user_data[0]["collection_count"] = collection_count

            data += serialized_user_data

        return Response(data)


users_followers_view = UserFollowersView.as_view()


# Returns the collections that a specific user has made
class UserCollectionsView(APIView):
    def get_User(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def get(self, request, pk, format=None):
        user = self.get_User(pk)
        collections = Collection.objects.filter(author=user).values('created', 'name', 'description', 'id', 'permission')

        return Response({'author_username': user.username, 'author_first': user.first_name, 'author_last': user.last_name, 'author_name': user.name, 'collections': list(collections)})

users_collections_view = UserCollectionsView.as_view()


class UserPictureView(APIView):
    parser_classes = (MultiPartParser, FormParser, )

    def get_User(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        user = self.get_User(pk)
        image_file = self.request.data.get('image')

        user.image = image_file
        user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data)

    # Test Route to open the current user's image and see url of current image
    def get(self, request, pk, format=None):
        user = self.get_User(pk)

        pre_im = PIL.Image.open(user.image)
        pre_im.show()

        return Response({"image url: " : str(user.image)})

user_picture_view = UserPictureView.as_view()


class TopicView(APIView):
    def get(self, request, topic_name, format=None):
        # topic_name = request.data['topic_name']
        collections = Topic.objects.filter(name__iexact=topic_name, collection__permission="Public").values_list('collection', flat=True)

        cList = []
        for collection in collections:
            search = Collection.objects.filter(pk=collection).values('created', 'author', 'name', 'description', 'id', 'permission')
            data = list(search)
            data[0]["author"] = UserPartSerializer(User.objects.get(pk=data[0]["author"])).data
            cList += data


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
    def get_User(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404("User does not exist")

    def get(self, request, pk, format=None):
        collection = self.get_User(pk)
        cs = CollectionSerializer(collection)
        links = Link.objects.filter(collection=collection).values('created', 'owner', 'url', 'collection', 'description')
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
        permission = request.data['permission']

        owner = User.objects.get(pk=owner_id)

        seenLinks = []
        if urls:
            for linkObj in urls:
                if linkObj['url'] in seenLinks:
                    return Response({'detail': 'No duplicate links allowed!'}, status=HTTP_400_BAD_REQUEST)

                seenLinks.append(linkObj['url'])

        if permission not in CollectionPermission.__members__:
            return Response({'detail': 'Collection permission not valid!'}, status=HTTP_400_BAD_REQUEST)

        # Create new collection object
        collection = Collection(author=owner, name=name, description=description, permission=permission)
        collection.save()

        data = {}
        data["collectionInfo"] = CollectionSerializer(collection).data

        links = []
        topicsRet = []
        if urls:
            for linkObj in urls:
                print(linkObj["url"])
                print(linkObj["description"])

                tempLink = Link(owner=owner, url=linkObj["url"], collection=collection, description=linkObj["description"])
                print("hi" + linkObj["url"])
                tempLink.save()
                links.append(LinkSerializer(tempLink).data)

        if topics:
            for topic in topics:
                print("topic: {}".format(topic))
                tempTopic = Topic(name=topic, collection=collection)
                tempTopic.save()
                topicsRet.append(topic)

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
    def get_User(self, pk):
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
        permission = request.data['permission']

        id_filter = Q(id=collection_id)
        author_filter = Q(author=owner_id)

        if not Collection.objects.filter(id_filter, author_filter):
            return Response({'detail': 'Collection does not exist for specified user!'}, status=HTTP_400_BAD_REQUEST)

        seenLinks = []
        if urls:
            for linkObj in urls:
                if linkObj['url'] in seenLinks:
                    return Response({'detail': 'No duplicate links allowed!'}, status=HTTP_400_BAD_REQUEST)

                seenLinks.append(linkObj['url'])

        if permission not in CollectionPermission.__members__:
            return Response({'detail': 'Collection permission not valid!'}, status=HTTP_400_BAD_REQUEST)

        collection = Collection.objects.get(pk=collection_id)
        collection.name = name
        collection.description = description
        collection.permission = permission

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
        for linkObj in urls:
            print("Adding {} to db...".format(linkObj["url"]))
            newLink = Link(owner=owner, url=linkObj["url"], collection=collection, description=linkObj["description"])
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
            topicsRet.append(topic)

        data["links"] = links
        data["topics"] = topicsRet

        return Response(data)

edit_collection_view = EditCollectionView.as_view()

# Add or delete link from collection
class LinkView(APIView):
    def linkExists(self, userId, collectionId, url):
        return Link.objects.filter(owner__id=userId, collection__id=collectionId, url=url)

    def post(self, request, format=None):
        user_id = request.data['user_id']
        collection_id = request.data['collection_id']
        link = request.data['link']

        targetCollection = Collection.objects.get(pk=collection_id)
        owner = User.objects.get(pk=user_id)

        if self.linkExists(user_id, collection_id, link['url']):
            return Response({'detail': 'Link already exists in collection!'}, status=HTTP_400_BAD_REQUEST)

        newLink = Link(owner=owner, url=link['url'], collection=targetCollection, description=link['description'])

        newLink.save()

        newCollectionLinks = Link.objects.get(owner__id=user_id, collection__id=collection_id, url=link['url'])

        return Response(LinkSerializer(newCollectionLinks).data)

    def delete(self, request, format=None):
        user_id = request.data['user_id']
        collection_id = request.data['collection_id']
        url = request.data['url']

        toDelete = Link.objects.filter(owner__id=user_id, collection__id=collection_id, url=url)

        toDelete.delete()

        return Response(status=HTTP_200_OK)

link_view = LinkView.as_view()

class EditLinkView(APIView):
    def getLink(self, userId, collectionId, url):
        return Link.objects.filter(owner__id=userId, collection__id=collectionId, url=url)

    def post(self, request, format=None):
        user_id = request.data['user_id']
        collection_id = request.data['collection_id']
        link = request.data['link']

        targetCollection = Collection.objects.get(pk=collection_id)
        owner = User.objects.get(pk=user_id)

        if not self.getLink(user_id, collection_id, link['url']):
            return Response({'detail': 'Link does not exist in collection!'}, status=HTTP_400_BAD_REQUEST)

        currLink = self.getLink(user_id, collection_id, link['url'])[0]

        currLink.description = link['description']

        currLink.save()

        newCollectionLinks = Link.objects.get(owner__id=user_id, collection__id=collection_id, url=link['url'])

        return Response(LinkSerializer(newCollectionLinks).data)

edit_link_view = EditLinkView.as_view()

# Returns all collections that are connected to the one requested based on id
class CollectionConnectedView(APIView):
    def get_User(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        collection = self.get_User(pk)

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
    def get_User(self, pk):
        try:
            return Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        collection_id = request.data['collectionFrom']
        collection_id2 = request.data['collectionTo']
        relation = request.data['relationship']

        collectionFrom = self.get_User(collection_id)
        collectionTo = self.get_User(collection_id2)

        if relation not in Relationship.__members__:
            return Response({'detail': 'Collection relationship not valid.'}, status=HTTP_400_BAD_REQUEST)

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


# Should move to their own files — here for now
def searchTopic(query):
    if not query:
        return Topic.objects.values_list('name', flat=True).distinct()

    return Topic.objects.filter(name__istartswith=query).values_list('name', flat=True).distinct()
