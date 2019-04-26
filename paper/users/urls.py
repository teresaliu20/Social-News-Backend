from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

# Boilerplate views
# user_list_view,
# user_redirect_view,
# user_update_view,
# user_detail_view,
from paper.users.views import (
    user_information_view,
    user_picture_view,
    edit_user_view,
    search_users_view,
    search_collections_view,
    users_collections_view,
    user_reading_list_view,
    users_following_view,
    topic_view,
    create_topic_view,
    search_topics_view,
    all_topics_view,
    collection_view,
    edit_collection_view,
    link_view,
    collection_connected_view,
    collection_relationship_view,
    signup_view,
    login_view,
    logout_view
)

app_name = "api"
urlpatterns = [
    path("login", view=login_view, name='userslogin'),
    path("signup", view=signup_view, name='usersignup'),
    path("logout", view=logout_view, name='userslogout'),
    url(r'^users/(?P<pk>[0-9]+)/collections', users_collections_view, name='usercollections'),
    url(r'^users/(?P<pk>[0-9]+)/reading-list', user_reading_list_view, name='userreadinglist'),
    url(r'^users/(?P<pk>[0-9]+)/profilepicture', user_picture_view, name='user-profile-picture'),
    url(r'^users/(?P<pk>[0-9]+)/following', users_following_view, name='user-followers'),
    url(r'^users/reading-list', user_reading_list_view, name='userreadinglist'),
    url(r'^users/edit', edit_user_view, name='edituser'),
    url(r'^users/search', search_users_view, name='searchuser'),
    url(r'^users', user_information_view, name='userinformation'),
    url(r'^collections/(?P<pk>[0-9]+)/connected', collection_connected_view, name='fromtoconnections'),
    url(r'^collections/relationship', collection_relationship_view, name='collectioninfo'),
    url(r'^collections/edit', edit_collection_view, name='editcollection'),
    url(r'^collections/(?P<pk>[0-9]+)', collection_view, name='collectioninfo'),
    url(r'^collections/search', search_collections_view, name='searchcollections'),
    url(r'^collections/link', link_view, name='collection-link-modifier'),
    url(r'^collections', collection_view, name='collectioninfo'),
    url(r'^topic/(?P<topic_name>[a-zA-Z0-9 !^&()_+\-=\[\]{}\':"\\|,.\/?]+)', topic_view, name='topiccollections'),
    url(r'^topics/search', search_topics_view, name='searchtopics'),
    url(r'^topics/all', all_topics_view, name='alltopics'),
    url(r'^topics/create', create_topic_view, name='alltopics')
]

urlpatterns = format_suffix_patterns(urlpatterns)
