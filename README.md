# Django 5.2 + Python 3.13 + MongoDB 6.x - Blog Application

A modern, full-featured blog application demonstrating the integration of Django 5.2 with MongoDB 6.x using MongoEngine ODM. This project showcases how to build a scalable web application using Django's powerful framework with MongoDB's flexible document database.

## 📋 Description

This blog application provides a complete content management system with the following capabilities:

### Core Features
- **Multi-Author Blog System**: Support for multiple authors with individual profiles
- **Rich Content Management**: Blog posts with categories, tags, and SEO optimization
- **Comment System**: Embedded comments with moderation and approval workflow
- **Newsletter Management**: Email subscription system with activation/deactivation
- **Search Functionality**: Full-text search across posts and content
- **Analytics Dashboard**: View counts, engagement metrics, and site statistics

### Technical Highlights
- **Document-Oriented Design**: Leverages MongoDB's document structure for embedded comments and flexible schemas
- **MongoEngine ODM**: Type-safe document modeling with validation and indexing
- **RESTful API**: JSON API endpoints for frontend integration
- **SEO Optimized**: Automatic slug generation, meta tags, and search-friendly URLs
- **Scalable Architecture**: Designed for high-traffic blogs with proper indexing and pagination

### Use Cases
- Personal or corporate blogs
- News and magazine websites
- Portfolio websites with blog functionality
- API backend for headless CMS implementations
- Learning project for Django + MongoDB integration

## 🛠 Tech Stack

- **Backend Framework**: Django 5.2
- **Database**: MongoDB 6.x
- **ODM**: MongoEngine (Document-Object Mapper)
- **Python Version**: 3.13
- **Authentication**: Django's built-in auth with MongoEngine backend
- **Session Management**: MongoDB-based sessions

## 🚀 Installation Guide

### Step 1: Install System Dependencies

#### Install Python 3.13

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-dev
```

**macOS (with Homebrew):**
```bash
brew install python@3.13
```

**Windows:**
Download and install from [python.org](https://www.python.org/downloads/)

#### Install MongoDB 6.x

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

**Windows:**
Download and install from [MongoDB Download Center](https://www.mongodb.com/try/download/community)

### Step 2: Project Setup

```bash
# Create project directory
mkdir django-mongo-blog
cd django-mongo-blog

# Create and activate virtual environment
python3.13 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install Django==5.2
pip install mongoengine
pip install pymongo[srv]
pip install python-decouple
pip install django-cors-headers
```

### Step 3: Create Django Project

```bash
# Create Django project
django-admin startproject myproject .

# Create blog application
python manage.py startapp blog

# Create directories for templates and static files
mkdir templates static media
```

### Step 4: Environment Configuration

Create `.env` file in project root:
```env
SECRET_KEY=your-very-long-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_DB_NAME=myblog
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USERNAME=
MONGO_PASSWORD=
```

### Step 5: Configure Django Settings

Update `myproject/settings.py` with MongoDB configuration and MongoEngine setup.

### Step 6: Create Models and Views

Set up MongoEngine models for Author, BlogPost, Tag, Category, and Newsletter in `blog/models.py`.
Create corresponding views in `blog/views.py` for handling blog functionality.

### Step 7: URL Configuration

Configure URL patterns for blog routes and API endpoints.

### Step 8: Run the Application

```bash
# Verify setup
python manage.py check

# Start development server
python manage.py runserver

# Access application at http://127.0.0.1:8000/
```

## 🔗 URL Structure & Views

### Main Blog URLs

| URL Pattern | View Function | Description |
|-------------|---------------|-------------|
| `/` | `home` | Homepage with featured and recent posts |
| `/posts/` | `post_list` | Paginated list of all published posts |
| `/post/<slug>/` | `post_detail` | Individual post detail page |
| `/author/<username>/` | `posts_by_author` | Posts filtered by specific author |
| `/tag/<slug>/` | `posts_by_tag` | Posts filtered by specific tag |
| `/category/<slug>/` | `posts_by_category` | Posts filtered by category |
| `/search/` | `search_posts` | Search results page |
| `/stats/` | `stats_dashboard` | Analytics and statistics dashboard |

### API Endpoints

| URL Pattern | View Function | Method | Description |
|-------------|---------------|--------|-------------|
| `/api/posts/` | `api_posts` | GET | JSON list of posts with pagination |
| `/api/post/<slug>/` | `api_post_detail` | GET | JSON single post detail |
| `/post/<slug>/comment/` | `add_comment` | POST | Add comment to post |
| `/newsletter/signup/` | `newsletter_signup` | POST | Newsletter subscription |

### View Functions Overview

#### Core Blog Views
- **`home(request)`**: Displays featured posts and recent posts on homepage
- **`post_list(request)`**: Shows paginated list of published posts with sidebar
- **`post_detail(request, slug)`**: Renders individual post with comments and related posts
- **`posts_by_author(request, username)`**: Lists posts by specific author
- **`posts_by_tag(request, slug)`**: Shows posts tagged with specific tag
- **`posts_by_category(request, slug)`**: Displays posts in specific category

#### Interactive Features
- **`add_comment(request, slug)`**: Handles comment submission with validation
- **`newsletter_signup(request)`**: Manages email subscription/unsubscription
- **`search_posts(request)`**: Processes search queries and returns results

#### Analytics & API
- **`stats_dashboard(request)`**: Provides site statistics and metrics
- **`api_posts(request)`**: RESTful API for posts with pagination
- **`api_post_detail(request, slug)`**: JSON API for single post data

### URL Configuration Files

**Main URLs (`myproject/urls.py`):**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Blog URLs (`blog/urls.py`):**
```python
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Filtered views
    path('author/<str:username>/', views.posts_by_author, name='posts_by_author'),
    path('tag/<slug:slug>/', views.posts_by_tag, name='posts_by_tag'),
    path('category/<slug:slug>/', views.posts_by_category, name='posts_by_category'),
    
    # Features
    path('search/', views.search_posts, name='search'),
    path('stats/', views.stats_dashboard, name='stats'),
    
    # API endpoints
    path('api/posts/', views.api_posts, name='api_posts'),
    path('api/post/<slug:slug>/', views.api_post_detail, name='api_post_detail'),
    
    # Interactive features
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
]
```

This URL structure provides a clean, SEO-friendly routing system that supports both traditional web views and modern API endpoints for potential frontend frameworks integration.