from django.conf import settings
from django.db import models

from accounts.models import TimeStampedModel


class News(TimeStampedModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news',
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title
