from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from .forms import PostForm

AMT_POSTS: int = 10


def index(request):
    posts = Post.objects.select_related('group')
    paginator = Paginator(posts, AMT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'posts': posts,
        'title': title,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    title = f'Записи сообщества: {group.title}'
    posts = group.posts.all()
    paginator = Paginator(posts, AMT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
        'title': title,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(
        author__username=username)
    paginator = Paginator(posts, AMT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Профайл пользователя {author.get_full_name()}'
    context = {
        'page_obj': page_obj,
        'title': title,
        'posts': posts,
        'username': username,
        'author': author,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    context = {
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    title = 'Новая запись'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
    form = PostForm()
    context = {
        'title': title,
        'form': form,
    }
    return render(request, template, context)


def post_edit(request, post_id):
    template = 'posts/post_create.html'
    post_data = Post.objects.get(id=post_id)
    form = PostForm(instance=post_data)
    is_edit = True
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)
