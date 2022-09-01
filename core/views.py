from genericpath import exists
from re import U
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowerCount
from django.contrib.auth.decorators import login_required
from itertools import chain
import random 

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    profile_user = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowerCount.objects.filter(follower=request.user.username)
    for user in user_following:
        user_following_list.append(user.user)
    for username in user_following_list:
        feed_list = Post.objects.filter(user=username)
        feed.append(feed_list)
    feed_list = list(chain(*feed))

    user_all = User.objects.all()
    user_following_all = []
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    user_suggestion = [x for x in list(user_all) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion = [x for x in list(user_suggestion) if (x not in list(current_user))]
    random.shuffle(final_suggestion)


    user_profile = []
    user_profile_list = []

    for user in final_suggestion:
        user_profile.append(user.id)
    
    for ids in user_profile:
        profile_list = Profile.objects.filter(id_user=ids)
        user_profile_list.append(profile_list)
    
    suggestions_username_profile = list(chain(*user_profile_list))
    user_profile_list = list(user_profile_list)

    context = {
        'user_profile': profile_user, 
        'posts': feed_list,
        'suggestions_username_profile': suggestions_username_profile[:4],
        'leng': len(suggestions_username_profile)
        }

    
    return render(request, 'index.html', context)

def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method=="POST":
        username = request.POST['username']
        username_object = User.objects.filter(username__contains=username)
        username_profile_list = []
        username_profile = []
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_list = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_list)
        
        username_profile_list = list(chain(*username_profile_list))

    context = {
        'user_profile': user_profile,
        'username_profile_list': username_profile_list
    }
    return render(request, 'search.html', context)

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile objec for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

        
    else:
        return render(request, 'signup.html')

@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']
        if FollowerCount.objects.filter(follower=follower,user=user).first():
            delete_follower = FollowerCount.objects.filter(follower=follower,user=user).first()
            delete_follower.delete()
            return redirect('profile', pk=user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('profile', pk=user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.filter(username=pk).first()
    user_profile = Profile.objects.get(user=user_object)
    user_post = Post.objects.filter(user=pk)
    len_post = len(user_post)

    follower = request.user.username
    user = pk
    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    user_follower = len(FollowerCount.objects.filter(user=pk))
    user_following = len(FollowerCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_post': user_post,
        'len_post': len_post,
        'button_text': button_text,
        'user_following': user_following,
        'user_follower': user_follower
    }
    return render(request, 'profile.html', context)

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')


    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == "POST":
        print(user_profile.user.username)
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image 
            user_profile.bio = bio 
            user_profile.location = location 
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image 
            user_profile.bio = bio 
            user_profile.location = location 
            user_profile.save()
        return redirect('settings')
            
    return render(request, 'setting.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method=='POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('index')
    else:
        return redirect('index')

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect('index')
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('index')
    