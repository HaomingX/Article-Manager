from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    summary = models.TextField()
    keywords = models.CharField(max_length=200)
    publish_time = models.DateTimeField(auto_now_add=True)  # 自动设置为添加时的时间
    content = models.TextField()

    def __str__(self):
        return self.title
