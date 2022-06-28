from django import forms
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Group, Post, User

from .forms import PostForm

def index(request):
    posts = Post.objects.all()
    # Показывать по 10 записей на странице
    paginator = Paginator(posts, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:settings.POST_PER_DATE]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # функция getobj получает по заданным критериям объект из базы данных 
    author = get_object_or_404(User, username=username)
    # отфильтровываем по авторы посты
    posts = author.posts.select_related('group', 'author')
    paginator = Paginator(posts, 10)
    posts_count = posts.count()
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = { 
              'page_obj': page_obj,
              'posts_count': posts_count,
              'author': author,
    }
    return render(request, 'posts/profile.html', context)

@login_required
def post_detail(request, post_id):
    # Страница для просмотра одного поста
    # Здесь код запроса к модели и создание словаря контекста
    # В пост выведен один пост, выбранный по pk
    post = get_object_or_404(Post, pk=post_id)
    # Выведено общее количество постов пользователя
    posts_count = Post.objects.filter(author=post.author).count()
    # В тег <title> выведен текст Пост < Первые 30 символов поста>
    context = { 'post': post,
                'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def post_create(request):
    '''Страница для публикации постов'''
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            form.save()
            return redirect('posts:profile',username=post.author)

        return render(request, 'posts/create_post.html', {'form':form})
    
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form':form})

def post_edit(request, post_id):
    '''страницу редактирования записи'''
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return rederict ('posts:post_detail.html')
    else:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('posts:post_detail', id=post_id)
            else:
                form = PostForm(instance=post)
        return render(request, 'posts/create_post.html', {'form': form,
                                                          'is_edit': True})
    


