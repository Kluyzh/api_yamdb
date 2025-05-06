from django.contrib import admin

from .models import Comment, Review, Category, Genre, Title


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug'
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug'
    )


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'display_genre', 'description', 'category', 'year'
    )

    @admin.display(description='Genres')
    def display_genre(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'author', 'review', 'pub_date'
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'text', 'author', 'score', 'pub_date'
    )
