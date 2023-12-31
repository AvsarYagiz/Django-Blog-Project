from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from django.views import View

from .models import Post
from .forms import CommentForm


class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        # Retrieve the three most recent posts
        queryset = super().get_queryset()
        data = queryset[:3]
        return data


class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "all_posts"


class SinglePostView(View):
    def get(self, request, slug):
        # Retrieve a single post and related information for rendering
        post = Post.objects.get(slug=slug)
        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": CommentForm(),
            "comments": post.comments.all()
        }
        return render(request, "blog/post-detail.html", context)

    def post(self, request, slug):
        # Handle POST request to add a comment to a post
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)

        if comment_form.is_valid():
            # Save the comment associated with the post
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()

            # Redirect to the post detail page after successfully adding a comment
            return HttpResponseRedirect(reverse("post-detail-page", args=[slug]))

        # If the comment form is not valid, re-render the post detail page with the form and existing comments
        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": comment_form,
            "comments": post.comments.all()
        }

        return render(request, "blog/post-detail.html", context)


class ReadLaterView(View):
    def get(self, request):
        # Handle GET request to display posts saved for later
        stored_posts = request.session.get("stored_posts")

        context = {}

        if stored_posts is None or len(stored_posts) == 0:
            # If no posts are stored, set context variables accordingly
            context["posts"] = []
            context["has_posts"] = False
        else:
            # Retrieve and display the posts saved for later
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True

        return render(request, "blog/stored-posts.html", context)

    def post(self, request):
        # Handle POST request to add a post to the "read later" list
        stored_posts = request.session.get("stored_posts")

        if stored_posts is None:
            # If no stored posts, initialize an empty list
            stored_posts = []

        post_id = int(request.POST["post_id"])

        if post_id not in stored_posts:
            # If the post is not already in the list, add it
            stored_posts.append(post_id)
            request.session["stored_posts"] = stored_posts

        # Redirect to the home page after successfully adding a post to the "read later" list
        return HttpResponseRedirect("/")
