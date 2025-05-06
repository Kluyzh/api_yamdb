from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

User = get_user_model()


admin.site.unregister(Group)


@admin.register(User)
class ModifiedUserAdmin(UserAdmin):
    model = User
    list_display = (
        'username', 'email', 'role', 'bio', 'is_admin', 'is_moderator',
        'review_count', 'comment_count'
    )
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

    @admin.display(description='Кол-во рецензий')
    def review_count(self, obj):
        return obj.reviews.count()

    @admin.display(description='Кол-во комментариев')
    def comment_count(self, obj):
        return obj.comments.count()
