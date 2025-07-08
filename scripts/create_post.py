from blog.models import User, Author, Category, Tag, BlogPost
from datetime import datetime

# Create a user and author
user = User.create_user(
    username="admin", email="admin@example.com", password="admin123"
)
print("✅ User created:", user.username)

author = Author.create_from_user(user)
print("✅ Author created:", author.username)

# Create category
category = Category(
    name="Technology", description="Posts about technology and programming"
).save()
print("✅ Category created:", category.name)

# Create tags
tag1 = Tag(name="Django").save()
tag2 = Tag(name="MongoDB").save()
tag3 = Tag(name="Python").save()
print("✅ Tags created: Django, MongoDB, Python")

# Create sample blog posts
post1 = BlogPost(
    title="Getting Started with Django and MongoDB",
    content="This is a comprehensive guide on how to set up Django with MongoDB using MongoEngine. MongoDB is a powerful NoSQL database that works great with Django...",
    author=author,
    category=category,
    is_published=True,
    is_featured=True,
    published_at=datetime.utcnow(),
)
post1.tags = [tag1, tag2, tag3]
post1.save()
print("✅ Post 1 created:", post1.title)

post2 = BlogPost(
    title="Advanced MongoDB Queries with MongoEngine",
    content="Learn how to perform complex queries using MongoEngine. This post covers aggregation, indexing, and optimization techniques...",
    author=author,
    category=category,
    is_published=True,
    published_at=datetime.utcnow(),
)
post2.tags = [tag2, tag3]
post2.save()
print("✅ Post 2 created:", post2.title)

post3 = BlogPost(
    title="Building RESTful APIs with Django",
    content="A complete guide to building RESTful APIs using Django. We will cover serialization, authentication, and best practices...",
    author=author,
    category=category,
    is_published=True,
    published_at=datetime.utcnow(),
)
post3.tags = [tag1, tag3]
post3.save()
print("✅ Post 3 created:", post3.title)

# Add some comments to the first post
post1.add_comment(
    author_name="John Doe",
    author_email="john@example.com",
    content="Great article! Very helpful for beginners.",
)

post1.add_comment(
    author_name="Jane Smith",
    author_email="jane@example.com",
    content="Thanks for the detailed explanation.",
)

# Approve comments
post1.comments[0].is_approved = True
post1.comments[1].is_approved = True
post1.save()
print("✅ Comments added and approved")

print("\n📊 Database Summary:")
print(f"Users: {User.objects.count()}")
print(f"Authors: {Author.objects.count()}")
print(f"Categories: {Category.objects.count()}")
print(f"Tags: {Tag.objects.count()}")
print(f"Posts: {BlogPost.objects.count()}")
print(f"Published Posts: {BlogPost.get_published().count()}")
