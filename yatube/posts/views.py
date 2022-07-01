from .utils import paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import Group, Post, User

from .forms import PostForm


def index(request):
    posts = Post.objects.all()
    context = {
        'page_obj': paginator(posts, request),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': paginator(posts, request),
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group', 'author')
    posts_count = posts.count()
    context = {
        'page_obj': paginator(posts, request),
        'posts_count': posts_count,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.select_related('author').count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Страница для публикации постов'''
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(False)
            post.author = request.user
            post = form.save()
            return redirect('posts:profile', username=post.author)

        return render(request, 'posts/create_post.html', {'form': form})

    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''страницу редактирования записи'''
    post = get_object_or_404(Post, pk=post_id)
    if post_id and request.user != post.author:
        return redirect('posts:profile', post_id=post_id)
    else:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post.save()
                return redirect('posts:post_detail', post_id=post_id)
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': True
        }
        return render(request, 'posts/create_post.html', context)
