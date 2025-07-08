from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    EmailField,
    DateTimeField,
    ListField,
    DictField,
    EmbeddedDocumentField,
    ReferenceField,
    IntField,
    BooleanField,
    URLField,
)
from datetime import datetime
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password, check_password
import secrets


class User(Document):
    """Custom User model using MongoEngine for authentication"""

    username = StringField(max_length=150, required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(max_length=128, required=True)  # Hashed password
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

    # User status
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    # Timestamps
    date_joined = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()

    # Profile fields
    bio = StringField(max_length=500)
    avatar_url = URLField()

    meta = {
        "collection": "users",
        "indexes": ["username", "email", "date_joined"],
        "ordering": ["-date_joined"],
    }

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if provided password matches hashed password"""
        return check_password(raw_password, self.password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    @classmethod
    def create_user(cls, username, email, password, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")

        user = cls(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def create_superuser(cls, username, email, password, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return cls.create_user(username, email, password, **extra_fields)


class Author(Document):
    """Author model for blog posts"""

    user = ReferenceField(User, required=True)  # Link to User
    username = StringField(max_length=50, required=True, unique=True)
    email = EmailField(required=True, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    bio = StringField(max_length=500)
    avatar_url = URLField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "authors",
        "indexes": ["username", "email", "created_at", "user"],
        "ordering": ["-created_at"],
    }

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    @classmethod
    def create_from_user(cls, user):
        """Create Author from User"""
        return cls(
            user=user,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
        ).save()


class Tag(Document):
    """Blog post tags"""

    name = StringField(max_length=50, required=True, unique=True)
    slug = StringField(max_length=50, required=True, unique=True)
    description = StringField(max_length=200)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "tags", "indexes": ["name", "slug"]}

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Category(Document):
    """Blog categories"""

    name = StringField(max_length=100, required=True, unique=True)
    slug = StringField(max_length=100, required=True, unique=True)
    description = StringField(max_length=300)
    parent = ReferenceField("self")  # Self-reference for sub-categories
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "categories", "indexes": ["name", "slug", "parent"]}

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Comment(EmbeddedDocument):
    """Embedded comment document"""

    author_name = StringField(max_length=100, required=True)
    author_email = EmailField(required=True)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    is_approved = BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.author_name}"


class BlogPost(Document):
    """Main blog post model"""

    title = StringField(max_length=200, required=True)
    slug = StringField(max_length=200, required=True, unique=True)
    content = StringField(required=True)
    excerpt = StringField(max_length=300)
    author = ReferenceField(Author, required=True)
    tags = ListField(ReferenceField(Tag))
    category = ReferenceField(Category)

    # SEO fields
    meta_title = StringField(max_length=60)
    meta_description = StringField(max_length=160)

    # Status and dates
    is_published = BooleanField(default=False)
    is_featured = BooleanField(default=False)
    published_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    # Engagement metrics
    view_count = IntField(default=0)
    like_count = IntField(default=0)

    # Comments (embedded)
    comments = ListField(EmbeddedDocumentField(Comment))

    # Additional metadata
    metadata = DictField()

    meta = {
        "collection": "blog_posts",
        "indexes": [
            "slug",
            "title",
            "author",
            "created_at",
            "published_at",
            "is_published",
            "is_featured",
            ("is_published", "-published_at"),
            ("author", "-created_at"),
        ],
        "ordering": ["-created_at"],
    }

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.excerpt and self.content:
            self.excerpt = (
                self.content[:297] + "..." if len(self.content) > 300 else self.content
            )

        if self.is_published and not self.published_at:
            self.published_at = datetime.utcnow()

        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    @property
    def approved_comments(self):
        return [comment for comment in self.comments if comment.is_approved]

    @property
    def comment_count(self):
        return len(self.approved_comments)

    def add_comment(self, author_name, author_email, content):
        comment = Comment(
            author_name=author_name, author_email=author_email, content=content
        )
        self.comments.append(comment)
        self.save()
        return comment

    def increment_view_count(self):
        self.view_count += 1
        self.save()

    @classmethod
    def get_published(cls):
        return cls.objects(is_published=True, published_at__lte=datetime.utcnow())

    @classmethod
    def get_featured(cls):
        return cls.objects(
            is_published=True, is_featured=True, published_at__lte=datetime.utcnow()
        )

    def get_related_posts(self, limit=3):
        """Get related posts excluding current post"""
        related = []

        # Get posts with same tags
        if self.tags:
            tag_posts = list(
                BlogPost.get_published().filter(tags__in=self.tags).limit(10)
            )
            # Filter out current post
            tag_posts = [p for p in tag_posts if p.id != self.id]
            related.extend(tag_posts[:limit])

        # Fill with author's other posts if needed
        if len(related) < limit:
            author_posts = list(
                BlogPost.get_published().filter(author=self.author).limit(10)
            )
            # Filter out current post and already included posts
            existing_ids = [p.id for p in related] + [self.id]
            author_posts = [p for p in author_posts if p.id not in existing_ids]
            related.extend(author_posts[: limit - len(related)])

        return related[:limit]


class Newsletter(Document):
    """Newsletter subscription model"""

    email = EmailField(required=True, unique=True)
    name = StringField(max_length=100)
    is_active = BooleanField(default=True)
    subscribed_at = DateTimeField(default=datetime.utcnow)
    unsubscribed_at = DateTimeField()

    meta = {
        "collection": "newsletter_subscribers",
        "indexes": ["email", "is_active", "subscribed_at"],
    }

    def __str__(self):
        return self.email


class UserSession(Document):
    """Custom session model for MongoDB"""

    session_key = StringField(max_length=40, required=True, unique=True)
    session_data = StringField(required=True)
    expire_date = DateTimeField(required=True)

    meta = {"collection": "user_sessions", "indexes": ["session_key", "expire_date"]}

    @classmethod
    def create_session(cls, session_key, session_data, expire_date):
        """Create or update session"""
        try:
            session = cls.objects.get(session_key=session_key)
            session.session_data = session_data
            session.expire_date = expire_date
            session.save()
        except cls.DoesNotExist:
            session = cls(
                session_key=session_key,
                session_data=session_data,
                expire_date=expire_date,
            ).save()
        return session


class SiteSettings(Document):
    """Site configuration"""

    site_name = StringField(max_length=100, default="My MongoDB Blog")
    site_description = StringField(max_length=300)
    site_url = URLField()
    admin_email = EmailField()
    posts_per_page = IntField(default=10)
    enable_comments = BooleanField(default=True)
    enable_newsletter = BooleanField(default=True)
    social_links = DictField()
    analytics_code = StringField()
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "site_settings"}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        settings = cls.objects.first()
        if not settings:
            settings = cls().save()
        return settings
