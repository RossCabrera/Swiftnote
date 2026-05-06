from django.contrib import admin

from .models import Category, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color_hex')
    list_filter = ('user',)
    search_fields = ('name',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at', 'is_archived')
    list_filter = ('is_archived', 'category', 'user')
    search_fields = ('title', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')