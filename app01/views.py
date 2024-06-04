from django.shortcuts import render, redirect
from .forms import ArticleForm
from .models import Article
import datetime
from django.http import JsonResponse, HttpResponseNotFound


def home(request):
    articles = Article.objects.all()
    current_date = datetime.date.today()
    current_date = current_date.strftime('%Y-%m-%d')

    total_articles = articles.count()
    return render(request, 'home.html', {'articles': articles, 'current_date': current_date, 'total_articles': total_articles})

def publish(request):
    form = ArticleForm()
    return render(request, 'publish.html', {'form': form})

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


