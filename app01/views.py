from django.shortcuts import render, redirect
from .forms import ArticleForm,UserRegisterForm, UserUpdateForm,CategoryForm
from .models import Article
import datetime
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import Category

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
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
    article = get_object_or_404(Article, id=article_id)
    user = str(request.user)
    # print("article.author", article.author, type(article.author))
    # print("user", user, type(user))
    if user != article.author:
        print("You are not authorized to edit this article.")
        messages.error(request, "You are not authorized to edit this article.")
        return redirect('personal')
    print("author edit article!")
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'The article has been updated.')
            return redirect('personal')
    else:
        form = ArticleForm(instance=article)
    context = {
        'form': form,
        'article': article,
    }
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