from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # ========================================================================
    # Main Blog Pages
    # ========================================================================
    # Homepage
    path("", views.home, name="home"),
    # Post listing and details
    path("posts/", views.post_list, name="post_list"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    # ========================================================================
    # Filtered Post Views
    # ========================================================================
    # Posts by author
    path("author/<str:username>/", views.posts_by_author, name="posts_by_author"),
    # Posts by tag
    path("tag/<slug:slug>/", views.posts_by_tag, name="posts_by_tag"),
    # Posts by category
    path("category/<slug:slug>/", views.posts_by_category, name="posts_by_category"),
    # ========================================================================
    # Search and Utility Pages
    # ========================================================================
    # Search functionality
    path("search/", views.search_posts, name="search"),
    # Statistics dashboard
    path("dashboard/", views.stats_dashboard, name="dashboard"),
    path("stats/", views.stats_dashboard, name="stats"),  # Alias
    # ========================================================================
    # Interactive Features
    # ========================================================================
    # Comment system
    path("post/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    # Newsletter subscription
    path("newsletter/signup/", views.newsletter_signup, name="newsletter_signup"),
    path("subscribe/", views.newsletter_signup, name="subscribe"),  # Alias
    # ========================================================================
    # API Endpoints
    # ========================================================================
    # RESTful API for posts
    path("api/posts/", views.api_posts, name="api_posts"),
    path("api/post/<slug:slug>/", views.api_post_detail, name="api_post_detail"),
    # ========================================================================
    # SEO and Utility URLs
    # ========================================================================
    # Sitemap (you can implement this later)
    # path('sitemap.xml', views.sitemap, name='sitemap'),
    # RSS feed (you can implement this later)
    # path('feed/', views.rss_feed, name='rss_feed'),
]
