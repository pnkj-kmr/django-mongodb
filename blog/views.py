from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
from mongoengine import DoesNotExist
from .models import BlogPost, Author, Tag, Category, Newsletter, SiteSettings, User
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Main Blog Views
# ============================================================================


def home(request):
    """Homepage with featured and recent posts"""
    try:
        # Get featured posts (limit 3)
        featured_posts = BlogPost.get_featured()[:3]

        # Get recent posts (limit 6)
        recent_posts = BlogPost.get_published().order_by("-published_at")[:6]

        # Get site settings
        site_settings = SiteSettings.get_settings()

        # Get categories for navigation
        categories = Category.objects.all()[:5]

        context = {
            "featured_posts": featured_posts,
            "recent_posts": recent_posts,
            "categories": categories,
            "site_settings": site_settings,
            "page_title": "Home",
        }
        return render(request, "blog/home.html", context)

    except Exception as e:
        logger.error(f"Error in home view: {e}")
        return render(request, "blog/error.html", {"error": "Unable to load homepage"})


def post_list(request):
    """List all published posts with pagination"""
    try:
        # Get all published posts
        posts_queryset = BlogPost.get_published().order_by("-published_at")

        # Simple pagination (you can enhance this)
        page = int(request.GET.get("page", 1))
        posts_per_page = 10
        start = (page - 1) * posts_per_page
        end = start + posts_per_page

        posts = list(posts_queryset[start:end])
        total_posts = posts_queryset.count()

        # Calculate pagination info
        has_next = end < total_posts
        has_previous = page > 1

        # Get sidebar data
        categories = Category.objects.all()
        tags = Tag.objects.all()
        recent_posts = BlogPost.get_published().order_by("-published_at")[:5]

        context = {
            "posts": posts,
            "categories": categories,
            "tags": tags,
            "recent_posts": recent_posts,
            "page": page,
            "has_next": has_next,
            "has_previous": has_previous,
            "next_page": page + 1 if has_next else None,
            "previous_page": page - 1 if has_previous else None,
            "site_settings": SiteSettings.get_settings(),
            "page_title": "All Posts",
        }
        return render(request, "blog/post_list.html", context)

    except Exception as e:
        logger.error(f"Error in post_list view: {e}")
        return render(request, "blog/error.html", {"error": "Unable to load posts"})


def post_detail(request, slug):
    """Individual post detail page"""
    try:
        # Get the post
        post = BlogPost.objects.get(slug=slug, is_published=True)

        # Increment view count
        post.increment_view_count()

        # Get related posts using the model method
        related_posts = post.get_related_posts(3)

        context = {
            "post": post,
            "related_posts": related_posts,
            "site_settings": SiteSettings.get_settings(),
            "page_title": post.title,
        }
        return render(request, "blog/post_detail.html", context)

    except DoesNotExist:
        raise Http404("Post not found")
    except Exception as e:
        logger.error(f"Error in post_detail view: {e}")
        return render(request, "blog/error.html", {"error": "Unable to load post"})


def posts_by_author(request, username):
    """Posts by specific author"""
    try:
        author = Author.objects.get(username=username)
        posts = BlogPost.get_published().filter(author=author).order_by("-published_at")

        context = {
            "author": author,
            "posts": posts,
            "site_settings": SiteSettings.get_settings(),
            "page_title": f"Posts by {author.full_name or author.username}",
        }
        return render(request, "blog/posts_by_author.html", context)

    except DoesNotExist:
        raise Http404("Author not found")
    except Exception as e:
        logger.error(f"Error in posts_by_author view: {e}")
        return render(
            request, "blog/error.html", {"error": "Unable to load author posts"}
        )


def posts_by_tag(request, slug):
    """Posts by specific tag"""
    try:
        tag = Tag.objects.get(slug=slug)
        posts = BlogPost.get_published().filter(tags=tag).order_by("-published_at")

        context = {
            "tag": tag,
            "posts": posts,
            "site_settings": SiteSettings.get_settings(),
            "page_title": f'Posts tagged "{tag.name}"',
        }
        return render(request, "blog/posts_by_tag.html", context)

    except DoesNotExist:
        raise Http404("Tag not found")
    except Exception as e:
        logger.error(f"Error in posts_by_tag view: {e}")
        return render(request, "blog/error.html", {"error": "Unable to load tag posts"})


def posts_by_category(request, slug):
    """Posts by specific category"""
    try:
        category = Category.objects.get(slug=slug)
        posts = (
            BlogPost.get_published().filter(category=category).order_by("-published_at")
        )

        context = {
            "category": category,
            "posts": posts,
            "site_settings": SiteSettings.get_settings(),
            "page_title": f'Posts in "{category.name}"',
        }
        return render(request, "blog/posts_by_category.html", context)

    except DoesNotExist:
        raise Http404("Category not found")
    except Exception as e:
        logger.error(f"Error in posts_by_category view: {e}")
        return render(
            request, "blog/error.html", {"error": "Unable to load category posts"}
        )


def search_posts(request):
    """Search posts by title or content"""
    query = request.GET.get("q", "").strip()
    posts = []

    try:
        if query:
            # Search in title first
            posts = list(
                BlogPost.get_published()
                .filter(title__icontains=query)
                .order_by("-published_at")
            )

            # If not enough results, search in content
            if len(posts) < 5:
                content_posts = list(
                    BlogPost.get_published()
                    .filter(content__icontains=query)
                    .order_by("-published_at")[:10]
                )
                # Remove already included posts
                existing_ids = [str(post.id) for post in posts]
                content_posts = [
                    p for p in content_posts if str(p.id) not in existing_ids
                ]
                posts.extend(content_posts)

        context = {
            "posts": posts,
            "query": query,
            "total_results": len(posts),
            "site_settings": SiteSettings.get_settings(),
            "page_title": f'Search Results for "{query}"' if query else "Search",
        }
        return render(request, "blog/search_results.html", context)

    except Exception as e:
        logger.error(f"Error in search_posts view: {e}")
        return render(request, "blog/error.html", {"error": "Search error"})


# ============================================================================
# Interactive Features
# ============================================================================


@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, slug):
    """Add comment to a post"""
    try:
        post = BlogPost.objects.get(slug=slug, is_published=True)

        # Parse request data
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST

        # Validate required fields
        required_fields = ["author_name", "author_email", "content"]
        for field in required_fields:
            if not data.get(field):
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"{field.replace('_', ' ').title()} is required",
                    },
                    status=400,
                )

        # Add comment
        comment = post.add_comment(
            author_name=data["author_name"].strip(),
            author_email=data["author_email"].strip(),
            content=data["content"].strip(),
        )

        response_data = {
            "status": "success",
            "message": "Comment added successfully! It will be visible after approval.",
        }

        # Return JSON for AJAX or redirect for form submission
        if request.content_type == "application/json":
            return JsonResponse(response_data)
        else:
            messages.success(request, response_data["message"])
            return HttpResponseRedirect(reverse("blog:post_detail", args=[slug]))

    except DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Post not found"}, status=404
        )

    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": "An error occurred while adding the comment",
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_signup(request):
    """Newsletter subscription"""
    try:
        # Parse request data
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST

        email = data.get("email", "").strip().lower()
        name = data.get("name", "").strip()

        if not email:
            return JsonResponse(
                {"status": "error", "message": "Email is required"}, status=400
            )

        # Check if already subscribed
        try:
            subscriber = Newsletter.objects.get(email=email)
            if subscriber.is_active:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "This email is already subscribed to our newsletter",
                    },
                    status=400,
                )
            else:
                # Reactivate subscription
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save()
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Welcome back! Your newsletter subscription has been reactivated.",
                    }
                )
        except DoesNotExist:
            # Create new subscription
            Newsletter(email=email, name=name).save()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Thank you for subscribing to our newsletter!",
                }
            )

    except Exception as e:
        logger.error(f"Error in newsletter signup: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": "An error occurred while subscribing. Please try again.",
            },
            status=500,
        )


# ============================================================================
# API Endpoints
# ============================================================================


def api_posts(request):
    """API endpoint for posts with pagination"""
    try:
        # Get query parameters
        page = int(request.GET.get("page", 1))
        limit = min(int(request.GET.get("limit", 10)), 50)  # Max 50 posts per page

        # Calculate offset
        offset = (page - 1) * limit

        # Get posts
        posts_queryset = BlogPost.get_published().order_by("-published_at")
        posts = list(posts_queryset[offset : offset + limit])
        total = posts_queryset.count()

        # Serialize posts
        posts_data = []
        for post in posts:
            posts_data.append(
                {
                    "id": str(post.id),
                    "title": post.title,
                    "slug": post.slug,
                    "excerpt": post.excerpt,
                    "author": {
                        "username": post.author.username,
                        "full_name": post.author.full_name,
                    },
                    "published_at": post.published_at.isoformat()
                    if post.published_at
                    else None,
                    "view_count": post.view_count,
                    "comment_count": post.comment_count,
                    "tags": [{"name": tag.name, "slug": tag.slug} for tag in post.tags],
                    "category": {"name": post.category.name, "slug": post.category.slug}
                    if post.category
                    else None,
                }
            )

        return JsonResponse(
            {
                "posts": posts_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit,
                    "has_next": offset + limit < total,
                    "has_previous": page > 1,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error in api_posts: {e}")
        return JsonResponse({"error": "Unable to fetch posts"}, status=500)


def api_post_detail(request, slug):
    """API endpoint for single post"""
    try:
        post = BlogPost.objects.get(slug=slug, is_published=True)

        # Increment view count
        post.increment_view_count()

        post_data = {
            "id": str(post.id),
            "title": post.title,
            "slug": post.slug,
            "content": post.content,
            "excerpt": post.excerpt,
            "author": {
                "username": post.author.username,
                "full_name": post.author.full_name,
                "bio": post.author.bio,
                "avatar_url": post.author.avatar_url,
            },
            "published_at": post.published_at.isoformat()
            if post.published_at
            else None,
            "updated_at": post.updated_at.isoformat(),
            "view_count": post.view_count,
            "like_count": post.like_count,
            "tags": [{"name": tag.name, "slug": tag.slug} for tag in post.tags],
            "category": {"name": post.category.name, "slug": post.category.slug}
            if post.category
            else None,
            "comments": [
                {
                    "author_name": comment.author_name,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                }
                for comment in post.approved_comments
            ],
            "seo": {
                "meta_title": post.meta_title,
                "meta_description": post.meta_description,
            },
        }

        return JsonResponse(post_data)

    except DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        logger.error(f"Error in api_post_detail: {e}")
        return JsonResponse({"error": "Unable to fetch post"}, status=500)


# ============================================================================
# Utility Views
# ============================================================================


def stats_dashboard(request):
    """Simple statistics dashboard"""
    try:
        # Calculate statistics
        total_posts = BlogPost.objects.count()
        published_posts = BlogPost.get_published().count()
        total_authors = Author.objects.count()
        total_tags = Tag.objects.count()
        total_categories = Category.objects.count()
        newsletter_subscribers = Newsletter.objects(is_active=True).count()

        # Calculate total views
        total_views = sum(post.view_count for post in BlogPost.objects.all())

        # Get recent posts
        recent_posts = BlogPost.objects.order_by("-created_at")[:5]

        # Get popular posts
        popular_posts = BlogPost.get_published().order_by("-view_count")[:5]

        stats = {
            "total_posts": total_posts,
            "published_posts": published_posts,
            "total_authors": total_authors,
            "total_tags": total_tags,
            "total_categories": total_categories,
            "newsletter_subscribers": newsletter_subscribers,
            "total_views": total_views,
            "recent_posts": recent_posts,
            "popular_posts": popular_posts,
        }

        context = {
            "stats": stats,
            "site_settings": SiteSettings.get_settings(),
            "page_title": "Dashboard",
        }

        return render(request, "blog/stats_dashboard.html", context)

    except Exception as e:
        logger.error(f"Error in stats_dashboard: {e}")
        return render(request, "blog/error.html", {"error": "Unable to load dashboard"})


def error_404(request, exception):
    """Custom 404 error page"""
    context = {
        "site_settings": SiteSettings.get_settings(),
        "page_title": "Page Not Found",
    }
    return render(request, "blog/404.html", context, status=404)


def error_500(request):
    """Custom 500 error page"""
    context = {
        "site_settings": SiteSettings.get_settings(),
        "page_title": "Server Error",
    }
    return render(request, "blog/500.html", context, status=500)
