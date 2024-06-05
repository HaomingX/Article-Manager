from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

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
    def __str__(self):
        return self.title
