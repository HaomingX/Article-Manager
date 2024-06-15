from django import forms
from .models import Article
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Comment
from ckeditor.widgets import CKEditorWidget
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name='default', attrs={'class': 'custom-content-class'}))
    class Meta:
        model = Article
        fields = ['title', 'author', 'summary', 'keywords', 'content','category','is_shared']  # 不包含 publish_time

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        # 设置 author 字段的默认值为当前登录的用户
        self.fields['author'].initial = self.instance.author if self.instance else None


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'level','parent']
    # parent.required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Enter your comment here...',
        'rows': 4,'cols': 40})
        }
