from django.conf import settings
from django.db import models


class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    cover_image_url = models.URLField(blank=True)
    published_at = models.DateTimeField()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField()
    banner_image_url = models.URLField(blank=True)

    # Pontos concedidos a quem faz check-in neste evento/lançamento.
    points_reward = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class CheckIn(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='check_ins')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='check_ins')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} @ {self.event.title}'
