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
    edit_user_view,
    find_users_view,
    users_collections_view,
    collection_view,
    edit_collection_view,
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
    url(r'^users/edit', edit_user_view, name='edituser'),
    url(r'^users/find', find_users_view, name='edituser'),
    url(r'^users', user_information_view, name='userinformation'),
    url(r'^collections/(?P<pk>[0-9]+)/connected', collection_connected_view, name='fromtoconnections'),
    url(r'^collections/relationship', collection_relationship_view, name='collectioninfo'),
    url(r'^collections/edit', edit_collection_view, name='editcollection'),
    url(r'^collections/(?P<pk>[0-9]+)', collection_view, name='collectioninfo'),
    url(r'^collections', collection_view, name='collectioninfo')
]

urlpatterns = format_suffix_patterns(urlpatterns)
