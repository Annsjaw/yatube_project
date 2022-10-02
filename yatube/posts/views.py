from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .support_def import paginator


def index(request):
    """Обработчик главной страницы"""
    posts = Post.objects.select_related('group')
    page_obj = paginator(request, posts)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Обработчик страницы подробной информации о группе"""
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('group')
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    """Обработчик страницы подробной информации автора"""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated and author.following.filter(
        user=request.user
    ).exists():
        following = True
    else:
        following = False
    posts = author.posts.select_related('author')
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Обработчик страницы подробной информации поста"""
    template = 'posts/post_detail.html'
    post = Post.objects.get(id=post_id)
    comments = post.comments.select_related('post')
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Обработчик страницы создания поста"""
    template = 'posts/post_create.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Обработчик страницы редактирования поста"""
    template = 'posts/post_create.html'
    post_data = get_object_or_404(Post, id=post_id)
    if request.user != post_data.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_data
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Блок добавления комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница с постами избранных авторов"""
    user = request.user  # текущий юзер
    posts = Post.objects.filter(
        author__following__user=user).select_related('author', 'group')
    page_obj = paginator(request, posts)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
        user=request.user, author=author
    ).exists():
        Follow.objects.create(user=request.user, author=author)
        return redirect('posts:profile', username)
    else:
        return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
