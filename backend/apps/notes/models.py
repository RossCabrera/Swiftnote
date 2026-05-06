import uuid

from django.conf import settings
from django.db import models


class Category(models.Model):
    """ Model to represent note categories for users """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='categories'
    )
    name = models.CharField(max_length=100)
    color_hex = models.CharField(max_length=7, default='#3b82f6') 

    class Meta:
        verbose_name_plural = "Categories"
        # Prevent a user from having two categories with the same name
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class Note(models.Model):
    """ Model to represent user notes """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notes'
    )

    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notes'
    )

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title