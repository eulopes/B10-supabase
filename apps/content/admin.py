from django.contrib import admin

from .models import CheckIn, Event, NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'points_reward')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'created_at')
    readonly_fields = ('user', 'event', 'created_at')
