# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from decouple import config
from .models import Post


def post_share(request, post_id):
    # Извлечь пост по индентификатору id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    sent = False

    if request.method == "POST":
        # форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # ...отправить электронное письмо
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cd["name"]} recommends you read"
                f"{post.title}"
            )
            message = (
                f"Read {post.title} at {post_url} \n\n"
                f"{cd["name"]}'s comments: {cd["comments"]}"
            )
            send_mail(
                subject,
                message,
                config("EMAIL_HOST_USER"),
                [cd["to"]],
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request,
        "blog/post/share.html",
        {
            "post": post,
            "form": form,
            "sent": sent
        }
    )


class PostListView(ListView):

    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 1
    template_name = "blog/post/list.html"


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    # список активный комментариев к посту
    comments = post.comments.filter(active=True)
    # форма для комментария пользователя
    form = CommentForm()

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
        }
    )


# def post_list(request):
#     post_list = Post.published.all()
#     paginator = Paginator(post_list, 1)
#     page_number = request.GET.get("page", 1)
#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#
#     return render(
#         request,
#         "blog/post/list.html",
#         {"posts": posts}
#     )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {
            "post": post,
            "form": form,
            "comment": comment
         }
    )
