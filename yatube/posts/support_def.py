from django.core.paginator import Paginator

AMT_POSTS: str = 10


def paginator(request, posts):
    paginator = Paginator(posts, AMT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
