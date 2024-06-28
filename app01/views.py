from django.shortcuts import render, redirect
from django.utils import timezone
from django.template.context_processors import csrf
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
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import csrf_exempt
from .llm_test import llm_explain, llm_chat
from django.core.cache import cache
from django.db.models import Q
import os
from django.conf import settings
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
    total_articles = 0
    for article in articles:
        if article.is_shared or article.author == request.user.username:
            total_articles += 1

    return render(request, 'home.html', {'articles': articles, 'current_date': current_date, 'total_articles': total_articles})

@login_required
def publish(request):
    if request.method == 'GET' and 'parentId' in request.GET:
        parent_id = request.GET['parentId']
        if parent_id:
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
    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }
    context.update(csrf(request))

    return render(request, 'article_detail.html',context)


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

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        article_id = data.get('article_id')

        # 根据文章ID获取文章内容
        article = Article.objects.get(id=article_id)
        article_content = article.content
        # 调用大模型函数进行对话
        response = llm_chat(article_content, message)

        return JsonResponse({'reply': response})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def personal(request):
    user_articles = Article.objects.filter(author=request.user)
    #print(user_articles)
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
                form = ArticleForm(post_data, instance=article)
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

    categories = Category.objects.all()
    if user != article.author:
        print("You are not authorized to edit this article.")
        messages.error(request, "You are not authorized to edit this article.")
        return redirect('personal')
    context = {
        'article': article,
        'categories': categories,
    }
    #print(article)
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
    category1 = Category.objects.filter(name=category)
    queryset = []
    for category in category1:
        if category.level !=3:
            category = Category.objects.filter(parent_id=category.id)
            queryset.extend(category)
    for category in queryset:
        if category.level !=3:
            category = Category.objects.filter(parent_id=category.id)
            queryset.extend(category)
    date = request.GET.get('date', '')
    current_date = datetime.date.today()
    current_date = current_date.strftime('%Y-%m-%d')

    q_objects = Q()
    if query:
        q_objects |= Q(content__icontains=query) | Q(title__icontains=query) | Q(category__name__icontains=query) \
                     | Q(author__icontains=query) | Q(keywords__icontains=query)

    if keyword:
        q_objects &= Q(keywords__icontains=keyword)

    if title:
        q_objects &= Q(title__icontains=title)
    if category:
        q_objects |= Q(category__name__icontains=category)
        if queryset:
            for category in queryset:
                q_objects |= Q(category__name__icontains=category)

    if date:
        q_objects &= Q(publish_time__date=date)

    articles = Article.objects.filter(q_objects)
    total_articles = 0
    for article in articles:
        if article.is_shared or article.author == request.user.username:
            total_articles += 1

    context = {
        'articles': articles,
        'current_date': current_date,
        'total_articles': total_articles,
    }
    return render(request, 'home.html', context)