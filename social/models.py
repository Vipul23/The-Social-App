from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os
from datetime import datetime

User = get_user_model()

def profileimage_saver(instance, filename):
    upload_to = 'profile_img'
    ext=filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    profileimg = models.ImageField(upload_to=profileimage_saver,default='profile_default.jpg')
    bio = models.TextField(blank=True)
    no_of_followers = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

def image_save_path(instance, filename):
    upload_to = 'post_img'
    ext=filename.split('.')[-1]
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return os.path.join(upload_to, filename)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to=image_save_path,blank=True)
    caption = models.CharField(blank=True,max_length=100)
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    no_of_comments = models.IntegerField(default=0)

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(default=datetime.now)

class Like(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)

class Relationship(models.Model):
    source = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower')
    target = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='following')
    relationship = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=datetime.now)