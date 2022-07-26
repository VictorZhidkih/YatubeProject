from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utils import paginator


@cache_page(20, key_prefix="index_page")
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
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group', 'author')
    following = Follow.objects.filter(user=request.user, author=author)
    posts_count = posts.count()
    context = {
        'page_obj': paginator(posts, request),
        'posts_count': posts_count,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    comments = Comment.objects.select_related(
        'author',
    )
    form = CommentForm()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    '''Страница для публикации постов'''
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    '''страницу редактирования записи'''
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:profile', username=post.author)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Страница добавления комментария"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        print(add_comment)
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Все посты автора на которого подписан текущий пользователь"""
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': paginator(posts, request),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Функция для подписки на автора"""
    author = get_object_or_404(User, username=username)
    currently_user = request.user
    follower = Follow.objects.filter(user=currently_user, author=author)
    if currently_user != author and not follower.exists():
        Follow.objects.create(user=currently_user, author=author)
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    currently_user = request.user
    follower = Follow.objects.filter(user=currently_user, author=author)
    if follower.exists():
        follower.delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)
