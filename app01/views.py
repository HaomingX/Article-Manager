from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import ArticleForm,UserRegisterForm, UserUpdateForm,CategoryForm, CommentForm
from .models import Article, Comment
import datetime
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import Category

import json
from django.views.decorators.csrf import csrf_exempt
from .llm_test import llm_explain
from django.core.cache import cache
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()
        print(form)
    return render(request, 'register.html', {'form': form})

def home(request):
    articles = Article.objects.all()
    current_date = datetime.date.today()
    current_date = current_date.strftime('%Y-%m-%d')

    total_articles = articles.count()
    return render(request, 'home.html', {'articles': articles, 'current_date': current_date, 'total_articles': total_articles})

@login_required
def publish(request):
    if request.method == 'GET' and 'parentId' in request.GET:
        parent_id = request.GET['parentId']
        subcategories = Category.objects.filter(parent_id=parent_id)
        data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
        return JsonResponse(data, safe=False)
    # article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        if 'name' in request.POST and 'level' in request.POST:
            name = request.POST['name']
            level = int(request.POST['level'])
            parent_id = request.POST.get('parent')
            if(parent_id=='null'):
                new_category = Category.objects.create(name=name, level=level, parent=None)
            else:
                parent = Category.objects.get(id=parent_id)
                new_category = Category.objects.create(name=name, level=level, parent=parent)
            return JsonResponse({'id': new_category.id, 'name': new_category.name})
        article_form = ArticleForm(request.POST, initial={"author": request.user})

        if article_form.is_valid():
            article_form.save()
            messages.success(request, 'Your article has been published!')
            return redirect('personal')
    else:
        article_form = ArticleForm(initial={"author": request.user})

    categories = Category.objects.all()
    context = {
        'article_form': article_form,
        'categories': categories,
    }
    # print(article_form)
    return render(request, 'publish.html', context)


@login_required
def submit_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ArticleForm()
    return render(request, 'publish.html', {'form': form})


# Read button
def article_content(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        content = article.content.replace('\n', '<br>')  # 替换换行符为<br>
        return JsonResponse({'content': content})
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = article.comments.filter(parent__isnull=True)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)
            new_comment.save()
            return redirect('article_detail', article_id=article.id)
    else:
        comment_form = CommentForm()

    return render(request, 'article_detail.html', {
        'article': article,
        'comments': comments,
        'comment_form': comment_form
    })


@csrf_exempt
def llm_explain_view(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        article = Article.objects.get(id=article_id)

        # Check if the summary is already cached
        cache_key = f'llm_summary_{article_id}'
        cached_summary = cache.get(cache_key)

        if cached_summary:
            summary = cached_summary
        else:
            summary = llm_explain(article.content)
            cache.set(cache_key, summary, timeout=60 * 60)  # Cache for 1 hour

        return JsonResponse({'summary': summary})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def personal(request):
    user_articles = Article.objects.filter(author=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            # 更新该用户的所有文章作者信息
            for article in user_articles:
                article.author = request.user.username
                article.save()
            messages.success(request, f'Your account has been updated!')
            #print('Your account has been updated!')
            return redirect('personal')
    else:
        user_form = UserUpdateForm(instance=request.user)

    context = {
        'user_form': user_form,
        'user_articles': user_articles,
    }
    return render(request, 'personal.html', context)


@login_required
def edit_article(request, article_id):
    if request.method == 'GET' and 'parentId' in request.GET:
        parent_id = request.GET['parentId']
        if parent_id !='':
            subcategories = Category.objects.filter(parent_id=parent_id)
            data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
        return JsonResponse(data, safe=False)
    article = get_object_or_404(Article, id=article_id)
    user = str(request.user)
    # print("article.author", article.author, type(article.author))
    # print("user", user, type(user))
    if request.method == 'POST':
        if 'name' in request.POST and 'level' in request.POST:
            name = request.POST['name']
            level = int(request.POST['level'])
            parent_id = request.POST.get('parent')
            if(parent_id=='null'):
                new_category = Category.objects.create(name=name, level=level, parent=None)
            else:
                parent = Category.objects.get(id=parent_id)
                new_category = Category.objects.create(name=name, level=level, parent=parent)
            return JsonResponse({'id': new_category.id, 'name': new_category.name})
        else:
            article = get_object_or_404(Article, id=article_id)
            if request.method == 'POST':
                # 获取 POST 数据
                post_data = request.POST.copy()  # 复制 POST 数据
                # 修改 POST 数据中的值
                name = request.POST.get('category')
                # messages.success(request, 'Your article has been edit!')
                subcategories = Category.objects.get(name=name)
                post_data['category'] = subcategories.id  # 将 'field_name' 字段的值修改为 'new_value'
                # 创建表单实例并传入修改后的 POST 数据
                # print(post_data)
                form = ArticleForm(post_data, instance=article)
                # print(form)
                if form.is_valid():
                    form.save()
                    print('success')
                    return redirect('personal')
                else:
                    print('form.is_not_valid')
            else:
                form = ArticleForm()
    article_form = ArticleForm(request.POST, initial={"author": request.user})
    if article_form.is_valid():
        print('author edit article!')
        article_form.save()
        messages.success(request, 'Your article has been published!')
        return redirect('personal')
    else:
        print('article_form.is_valid')

    categories = Category.objects.all()
    if user != article.author:
        print("You are not authorized to edit this article.")
        messages.error(request, "You are not authorized to edit this article.")
        return redirect('personal')
    context = {
        'article': article,
        'categories': categories,
    }
    print(article)
    return render(request, 'edit_article.html', context)


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = str(request.user)
    if user != article.author:
        print("You are not authorized to delete this article.")
        messages.error(request, "You are not authorized to delete this article.")
        return redirect('personal')
    print("author delete article!")

    article.delete()
    messages.success(request, "The article has been deleted.")
    return redirect('personal')


def search(request):
    query = request.GET.get('q', '')
    keyword = request.GET.get('keyword', '')
    title = request.GET.get('title', '')
    category = request.GET.get('category', '')
    date = request.GET.get('date', '')

    q_objects = Q()

    if query:
        q_objects |= Q(content__icontains=query) | Q(title__icontains=query) | Q(category__name__icontains=query) \
                     | Q(author__icontains=query) | Q(keywords__icontains=query)

    if keyword:
        q_objects &= Q(content__icontains=keyword)

    if title:
        q_objects &= Q(title__icontains=title)

    if category:
        q_objects &= Q(category__name__icontains=category)

    if date:
        q_objects &= Q(publish_time__date=date)

    articles = Article.objects.filter(q_objects)

    context = {
        'articles': articles,
        'date': timezone.now().date(),
        'total_articles': Article.objects.count(),
    }
    return render(request, 'home.html', context)