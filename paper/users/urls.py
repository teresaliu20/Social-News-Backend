from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from paper.users.views import (
    user_list_view,
    user_redirect_view,
    user_update_view,
    user_detail_view,
    bookmarks_list_view,
    users_list_view,
    user_bookmarks_view,
    users_feed_view,
    users_following_view,
    users_social_feed_view
)

app_name = "users"
urlpatterns = [
    path("", view=user_list_view, name="list"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path("all-bookmarks", view=bookmarks_list_view, name='bookmarks'),
    path("show-all", view=users_list_view, name='usersall'),
    path("<int:pk>/bookmarks", view=user_bookmarks_view, name='userbookmarks'),
    path("<int:pk>/explore-feed", view=users_feed_view, name='userexplorefeed'),
    path("<int:pk>/following", view=users_following_view, name='userfollowing'),
    path("<int:pk>/social-feed", view=users_social_feed_view, name='usersocialfeed')
]

urlpatterns = format_suffix_patterns(urlpatterns)
