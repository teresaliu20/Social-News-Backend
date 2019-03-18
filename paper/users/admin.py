from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from paper.users.forms import UserChangeForm, UserCreationForm
from .models import Following, Collection, Link, CollectionRelationship, Topic

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name", "bio", "linksProposed", "linksAccepted")}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "bio", "is_superuser"]
    search_fields = ["name"]


class FollowingAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'creator', 'following')


class LinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'owner', 'collection')


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'owner', 'name')


class CollectionRelationshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'start', 'end', 'relationship', 'approved')


class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'name', 'collection')


admin.site.register(Following, FollowingAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(CollectionRelationship, CollectionRelationshipAdmin)
admin.site.register(Topic, TopicAdmin)
