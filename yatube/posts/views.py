from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAG_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAG_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'paginator': paginator,
        'page': page,
    }
    return render(request, 'group.html', context)


@login_required()
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    paginator = Paginator(author_posts, settings.PAG_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post_count = author.posts.count()
    context = {
        'author': author,
        'page': page,
        'post_count': post_count,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    context = {
        'post': post,
        'author': author,
        'form': form,
    }
    return render(request, 'post.html', context)


@login_required()
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('post', username, post_id)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(
        request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PAG_POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    follower = request.user
    user_following = get_object_or_404(User, username=username)
    if follower != user_following:
        Follow.objects.get_or_create(user=request.user, author=user_following)
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    follower = request.user
    user_following = get_object_or_404(User, username=username)
    follow_objects = Follow.objects.filter(
        user=follower,
        author=user_following
    )
    if follow_objects.exists():
        follow_objects.delete()
    return redirect('follow_index')
