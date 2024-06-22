from django.contrib import admin
from .models import Category, Article, Comment

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'parent')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_time', 'is_shared', 'category')
    search_fields = ('title', 'author', 'summary', 'keywords')
    list_filter = ('is_shared', 'publish_time', 'category')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'publish_time', 'parent')
    search_fields = ('content', 'author__username', 'article__title')
    list_filter = ('publish_time',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
