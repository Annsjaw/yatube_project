from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .support_def import paginator
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    posts = Post.objects.select_related('group')
    page_obj = paginator(request, posts)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'posts': posts,  # Возможно не нужен
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('group')
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,  # Посмотреть можно все получить через page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,  # можно достать count из пагинатора page_obj.paginator.count
        'posts': posts,  # Посты можно посчитать через Paginator
        'username': username,  # Не используется в шаблоне
        'author': author,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(id=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
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
    template = 'posts/post_create.html'
    post_data = get_object_or_404(Post, id=post_id)
    if request.user != post_data.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post_data)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, template, context)
