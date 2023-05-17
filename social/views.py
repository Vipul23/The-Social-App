import re
import json
import datetime

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.contrib import messages,humanize
from django.contrib.auth import password_validation
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery, OuterRef

from .models import Profile, Post, Comment, Like, Relationship
# Create your views here.


def signup(request):
    if request.method == 'POST':
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        if password != password2:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
        elif password_validation.validate_password(password, user=User):
            messages.info(request, 'Password is too common')
            return redirect('signup')
        elif (re.match(pattern, password) is None):
            messages.info(
                request, 'Password does not fulfill the requirements')
            return redirect('signup')
        elif User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return redirect('signup')
        else:
            user = User.objects.create_user(
                username=username, password=password, email=email, first_name=f_name, last_name=l_name)
            user.save()

            user_login = auth.authenticate(
                username=username, password=password)
            auth.login(request, user_login)

            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(
                user=user_model, id_user=user_model.id, first_name=f_name, last_name=l_name)
            new_profile.save()
            return redirect('settings')
        return render(request, 'index.html')
    else:
        return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'login.html')


@login_required(login_url='/login')
def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required(login_url='/login')
def index(request):
    user_obj = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=request.user)
    # followed_authors = Relationship.objects.filter(source=user_profile, relationship='Follow').values('target')
    # posts = Post.objects.filter(author__in=Subquery(followed_authors))
    # return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})
    return render(request, 'index.html', {'user_profile': user_profile})

def prettydate(d):
    diff = datetime.datetime.now(datetime.timezone.utc) - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(s//60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(s//3600)

@login_required(login_url='/login')
def listing_api(request):
    user_obj = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=request.user)
    page_number = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 2)
    followed_authors = Relationship.objects.filter(source=user_profile, relationship='Follow').values('target')
    posts = Post.objects.filter(author__in=Subquery(followed_authors)).order_by("-created_at")
    # posts = Post.objects.all().order_by("-created_at")
    if (posts.exists()):
        paginator = Paginator(posts, per_page)
        page_obj = paginator.get_page(page_number)

        payload = {
            'page': {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(), },
            'posts': {
            },
        }
        post_rn=0
        for post in page_obj:
            post_rn+=1
            payload['posts'][str(post_rn)] = {
                "id": post.id,  
                "title": post.title,
                "content": post.content,
                "image": post.image.url if post.image else None,
                "caption": post.caption,
                "author": post.author.user.username,
                "author_id": post.author.id_user,
                "author_follow": Relationship.objects.filter(source=Profile.objects.get(user=request.user), target=post.author, relationship="Follow").exists(),
                "f_name": post.author.first_name,
                "l_name": post.author.last_name,
                "author_img": post.author.profileimg.url,
                "created_at": prettydate(post.created_at),
                "no_of_likes": post.no_of_likes,
                "no_of_comments": post.no_of_comments,
                "no_of_followers": post.author.no_of_followers,
                "is_liked": Like.objects.filter(author=Profile.objects.get(user=request.user), post=post).exists(),
                "is_user": True if user_obj == post.author.user else False,
            }
        return JsonResponse(payload)
    else:
        return JsonResponse({'page': {'current': 1, 'has_next': False, 'has_previous': False}, 'posts': {}, 'empty': True})

@login_required(login_url='/login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('profilepic') == None:
            img = user_profile.profileimg
        else:
            img = request.FILES.get('profilepic')

        first_name = request.POST['f_name']
        last_name = request.POST['l_name']
        username = request.POST['username']
        bio = request.POST['bio']
        location = request.POST['location']

        if (str(username) != str(user_profile.user)):
            if (User.objects.filter(username=username).exists()):
                messages.info(request, 'Username already exists')
                return redirect('settings')

        user_profile.user.username = username
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.profileimg = img
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

    return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='/login')
def newpost(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        caption = request.POST['caption']

        if request.FILES.get('postimage') == None:
            img = ""
        else:
            img = request.FILES.get('postimage')

        new_post = Post.objects.create(
            author=user_profile, title=title, content=content, image=img, caption=caption)
        new_post.save()

        return redirect('/')

    return render(request, 'newpost.html', {'user_profile': user_profile})

@login_required(login_url='/login')
def like(request):
    if request.method == 'GET':
        user_profile = Profile.objects.get(user=request.user)
        post_id = request.GET['postId']
        post_ch = Post.objects.get(id=post_id)
        isliked = Like.objects.filter(
            author=user_profile, post=post_ch).exists()
        if not isliked:
            new_like = Like.objects.create(
                author=user_profile, post=post_ch)
            new_like.save()
            post_ch.no_of_likes += 1
            post_ch.save()
            isliked = True
        else:
            Like.objects.filter(author=user_profile, post=post_ch).delete()
            post_ch.no_of_likes -= 1
            post_ch.save()
            isliked = False
        return JsonResponse({'like':isliked})

    return redirect('/')

@login_required(login_url='/login')
def comment(request, post_id):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        post_id = request.POST['postId']
        post_ch = Post.objects.get(id=post_id)
        content = request.POST['content']
        new_comment = Comment.objects.create(
            author=user_profile, post=post_ch, content=content)
        new_comment.save()
        post_ch.no_of_comments += 1
        post_ch.save()
        return redirect('/comments/'+post_id)
    comments=Comment.objects.filter(post=post_id)
    post_ch = Post.objects.get(id=post_id)
    return render(request, 'comments.html', {'user_profile': user_profile,'comments':comments,'post':post_ch})

@login_required(login_url='/login')
def follow(request):
    if request.method == 'GET':
        user_profile = Profile.objects.get(user=request.user)
        user_id = request.GET['userId']
        user_ch = Profile.objects.get(id_user=user_id)
        if user_profile == user_ch:
            return redirect('/')
        isfollowing = Relationship.objects.filter(
            source=user_profile, target=user_ch, relationship="Follow").exists()
        isunfollowing = Relationship.objects.filter(
            source=user_profile, target=user_ch, relationship="Unfollow").exists()

        if isunfollowing:
            Relationship.objects.filter(
                source=user_profile, target=user_ch, relationship="Unfollow").delete()
            new_follow = Relationship.objects.create(
                source=user_profile, target=user_ch, relationship="Follow")
            new_follow.save()
            user_ch.no_of_followers += 1
            user_ch.save()
            isfollowing = True
        elif isfollowing:
            Relationship.objects.filter(
                source=user_profile, target=user_ch, relationship="Follow").delete()
            new_unfollow = Relationship.objects.create(
                source=user_profile, target=user_ch, relationship="Unfollow")
            new_unfollow.save()
            user_ch.no_of_followers -= 1
            user_ch.save()
            isfollowing = False
        else:
            new_follow = Relationship.objects.create(
                source=user_profile, target=user_ch, relationship="Follow")
            new_follow.save()
            user_ch.no_of_followers += 1
            user_ch.save()
            isfollowing = True
        return JsonResponse({'follow':isfollowing})
    return redirect('/')

@login_required(login_url='/login')
def profile_page(request, username_ch):
    user_profile = Profile.objects.get(user=request.user)
    user_ch = User.objects.get(username=username_ch)
    profile_ch = Profile.objects.get(user=user_ch)
    
    return render(request, 'profile.html', {'user_profile': user_profile,'author_profile':profile_ch})
