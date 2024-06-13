from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE,related_name='children',null=True, blank=True )
    def __str__(self):
        return self.name
class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    summary = models.TextField()
    keywords = models.CharField(max_length=200)
    publish_time = models.DateTimeField(auto_now_add=True)  # 自动设置为添加时的时间
    content = models.TextField()
    category =  models.ForeignKey(Category, on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)  # 新增字段，默认值为 False（非共享状态）
    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    publish_time = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return self.content[:20] + '...'