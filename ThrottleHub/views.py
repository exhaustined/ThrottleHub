from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages as msg
from django.core.mail import send_mail
import random
from datetime import datetime, timedelta
from django.conf import settings
from .models import *
from django.db.models import Q
from django.http import JsonResponse


from json import loads
# Create your views here.
def index(request):
    posts = Posts.objects.all()
    context = {'posts': posts}
    if request.user.is_authenticated:
        profile = User.objects.get(id=request.user.id)
    garage = []
    for k in posts:
        j = User.objects.filter(id=k.owner_id).first()
        if j and j not in garage:
            garage.append(j)
    likes = Likes.objects.all()
    liked_posts = []
    for k in likes:
        if k.user_id == request.user.id:
            liked_posts.append(k.post_id)
    print("liked",liked_posts)
    context['liked_posts']=liked_posts
    if request.method=="POST":
        if request.POST.get('form_type') == 'form1':
            searchcontent=request.POST.get("searchcontent")
            # searchposts = Posts.objects.filter(Q(brand=searchcontent) | Q(model=searchcontent) | Q(licenseplate=searchcontent))
            request.session['searchposts'] = searchcontent
            return redirect(search)
        elif request.POST.get('form_type') == 'form2':
            comment = request.POST.get('comment')
            pid = request.POST.get('post')
            post = Posts.objects.get(id=pid)
            commented = Comment.objects.create(content=comment, post=post, author=profile)
            commented.save()
    context['garage'] = garage
    context['page'] = 'discover'
    return render(request, 'index.html', context)

def signin(request):
    if request.method=="POST":
        name=request.POST.get("name")
        password = request.POST.get("password")
        print(name,password)
        user = authenticate(request, username=name, password=password)
        if user is not None:
            login(request,user)
            return redirect(index)
        else:
            print("ERROR")
            msg.error(request,"Invalid credentials")
    return render(request,'login.html')

def register(request):
    if request.method=="POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        pic = request.FILES.get("profilepic")
        if password1 == password2:
            if User.objects.filter(username=name).exists():
                msg.error(request,"Username already exists")
            elif User.objects.filter(email=email).exists():
                msg.error(request, "Email already exists")

            else:
                user = User.objects.create_user(username=name, email=email, password=password1)
                user.save()
                user = User.objects.get(username=name)
                pp = ProfilePics.objects.create(user=user, image=pic)
                pp.save()
                print("ACCOUNT CREATED")
                return redirect(signin)
        else:
            msg.error(request, "The passwords don't match")
    return render(request,'register.html',)
def generate_otp():
    return random.randint(100000,999999)
def forget(request):
    if request.method=="POST":
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            otp=generate_otp()
            print("generated otp= ",otp)
            send_mail("Your OTP",f'Your otp is {otp}, it will expire in 5 mins',settings.EMAIL_HOST_USER,[email])
            request.session['otp']=otp
            request.session['time']=str(datetime.now())
            request.session['email']= email
            return redirect(verify_otp)
        else:
            messages.warning(request,"Email is not registered with us")

    return render(request, 'forgetpassword.html')


def verify_otp(request):
    send_otp = request.session.get('otp')
    send_time = request.session.get('time')
    email = request.session.get('email')
    time=datetime.strptime(send_time,'%Y-%m-%d %H:%M:%S.%f')
    delta=datetime.now()-time
    if request.method=="POST":
        otp = request.POST.get("otp")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if send_otp == int(otp) and delta <= timedelta(minutes=5):
            user = User.objects.get(email=email)
            user.set_password(str(password2))
            user.save()
            return redirect(signin)
        else:
            messages.warning(request, "Invalid OTP")
        if password1 != password2:
            messages.warning(request, "Passwords do not match")

    return render(request, 'newpassword.html')

def sign_out(request):
    logout(request)
    return redirect(index)


def upload_spot(request):
    # cars= loads("cars.json")
    # print(cars)
    if request.method=="POST":
        l_plate = request.POST.get("l_plate")
        l_plate_confirm = request.POST.get("l_plate_confirm")
        brand = request.POST.get("brand")
        model = request.POST.get("model")
        city = request.POST.get("city")
        desc = request.POST.get("desc")
        owner = request.POST.get("owner")
        image1 = request.FILES.get('image1')
        if owner != "on":
            try:
                owner = Garage.objects.get(licenseplate=l_plate)
                owner= owner.owner.id
                print("dfdf",owner)
            except:
                owner = 0
        else:
            owner = User.objects.get(id=request.user.id)
            owner = owner.id
            print("asdasdasdasd",owner)
        if l_plate == l_plate_confirm:
            spotter = User.objects.get(id=request.user.id)
            print(spotter)
            post = Posts.objects.create(spotter=spotter,images1=image1,licenseplate=l_plate,brand=brand,model=model,city=city,description=desc,owner_id=owner)
            post.save()
            return redirect(index)
        else:
            msg.error(request,"License number Mismatch!")

    # if request.method == 'POST' and request.FILES:
    #     # Handle uploaded files here
    #     for file in request.FILES.getlist('images'):
    #         pass
        # Process each uploaded image file
        # Example: Save the file to a specific location
        # file.name contains the name of the file
        # file.read() contains the file content
        # You can use Django's file handling utilities or libraries like PIL to process images

        # Redirect or render a success message
        # return render(request, 'upload_success.html')

    return render(request, 'upload_spot.html')

def profile(request):
    followed= request.session.get('followed')
    if followed:
        user = User.objects.get(username=followed)
        request.session.pop('followed')
    else:
        user=request.GET.get("username")
        if user is None:
            user=request.user
        else:
            user = User.objects.get(username=user)
    context={'user':user}
    if not request.user.is_authenticated:
        context['following'] = False
    elif user.id != request.user.id:

        following = Follows.objects.filter(user=user,followed_by= request.user)
        print("FOLLOWED CHECK ",following)
        if following.exists():
            context['following']=True
        else:
            context['following'] = False
        print(context['following'])
    posts = Posts.objects.filter(spotter_id=user.id)  # Returns a QuerySet
    if posts.exists():
        context['posts']= posts
    else:
        context['posts']= None
    context['post_count'] = len(posts)
    spots = Posts.objects.filter(owner_id=user.id)  # Returns a QuerySet
    if spots.exists():
        context['spots']= spots
    else:
        context['spots']= None

    garage = Garage.objects.filter(owner_id=user.id)  # Returns a QuerySet
    if garage.exists():
        context['garage']= garage
    else:
        context['garage']= None

    pic = ProfilePics.objects.filter(user_id=user.id).first()
    if pic:
        context['pic'] = pic
    else:
        context['pic'] = False

    if request.method=="POST":
        if request.POST.get('form_type') == 'form1':
            searchcontent=request.POST.get("searchcontent")
            # searchposts = Posts.objects.filter(Q(brand=searchcontent) | Q(model=searchcontent) | Q(licenseplate=searchcontent))
            request.session['searchposts'] = searchcontent
            return redirect(search)
    followers_count = Follows.objects.filter(user_id=user)
    following_count = Follows.objects.filter(followed_by_id=user)
    context['followers_count']= len(followers_count)
    context['following_count'] = len(following_count)
    return render(request, 'profile.html', context)

def add_to_garage(request):
    if request.method=="POST":
        licenseplate=request.POST.get("l_plate")
        licenseplate_confirm=request.POST.get("l_plate_confirm")
        if licenseplate== licenseplate_confirm:
            brand = request.POST.get("brand")
            model = request.POST.get("model")
            owner = User.objects.get(id=request.user.id)
            image = request.FILES.get('image')
            garage = Garage.objects.create(owner=owner, licenseplate=licenseplate, brand=brand, model=model,image=image)
            garage.save()
            return redirect(profile)
        else:
            msg.error(request, "License number doesnt match!")
    return render(request, 'add_to_garage.html')

def follow_request(request, following_id):
    user = User.objects.get(id=request.user.id)
    print("PRE",following_id)
    following_id = User.objects.get(id=following_id)
    print("POST", following_id)
    follow = Follows.objects.create(user=following_id,followed_by=user)
    follow.save()
    # followed = User.objects.get(username=following_id.username)
    request.session['followed']=following_id.username
    return redirect(profile)

def unfollow_request(request, following_id):
    user = User.objects.get(id=request.user.id)
    following_id = User.objects.get(id=following_id)
    unfollow = Follows.objects.get(user=following_id, followed_by=user)
    unfollow.delete()
    request.session['followed'] = following_id.username
    return redirect(profile)

def search(request):
    if request.method == "POST":
        searchcontent = request.POST.get("searchcontent").lower()
    else:
        searchcontent = request.session.get('searchposts').lower()
    if searchcontent:
        postcontent = Posts.objects.all()
        profilecontent = User.objects.all()
        searchposts = []
        profiles = []
        for k in postcontent:
            if (searchcontent in k.brand.lower() or  searchcontent in k.model.lower() or  searchcontent in k.licenseplate.lower()
                    or searchcontent in k.city.lower() or searchcontent in k.spotter.username.lower()):
                searchposts.append(k)
        for k in profilecontent:
            if searchcontent in k.username.lower():
                profiles.append(k)
    context = {'searchposts': searchposts,'searched':searchcontent,'profiles':profiles}
    pic = []
    for c in profiles:
        pp =ProfilePics.objects.filter(user_id=c.id).first()
        if pp and pp not in pic:
            pic.append(pp)
    context['pic'] = pic
    likes = Likes.objects.all()
    liked_posts = []
    for k in likes:
        if k.user_id == request.user.id:
            liked_posts.append(k.post_id)
    context['liked_posts'] = liked_posts
    garage = []
    for k in postcontent:
        j = User.objects.filter(id=k.owner_id).first()
        if j and j not in garage:
            garage.append(j)
    context['garage'] = garage
    context['page']='search'
    return render(request, 'search.html', context)


def messages(request,id):
    if not request.user.is_authenticated:
        return redirect('login')
    logged_in_user_id = request.user.id
    print(logged_in_user_id)
    user = User.objects.get(id=request.user.id)
    to_user = None
    threads = None
    prof = None
    if id is not None:
        to_user = User.objects.get(id=id)
        # prof = ProfilePics.objects.get(user=to_user)
        # print(prof.images)
        try:
            # Try to get existing thread between current user and the selected user
            thread = Thread.objects.get(first_person=user, second_person=to_user)
            print(1, thread)
        except Thread.DoesNotExist:
            try:
                # Try to get existing thread where the selected user is the first person
                thread = Thread.objects.get(first_person=to_user, second_person=user)
                print(2, thread)
            except Thread.DoesNotExist:
                # If no existing thread, create a new thread
                thread = Thread.objects.create(first_person=user, second_person=to_user)
                print(3, thread)
        finally:
            # Mark all unread messages as read
            unread_messages = ChatMessage.objects.filter(thread=thread, user=to_user, read=False)
            # print(unread_messages)
            for msg in unread_messages:
                msg.read = True
                msg.save()
        # if not ChatMessage.objects.filter(thread=thread, user=user).exists() and not ChatMessage.objects.filter(
        #     thread=thread, user=to_user).exists():
        #         chat1 = ChatMessage.objects.create(thread=thread,user=user,message="Welcome to ChatNest")
        #         chat1.save()
        #         chat2 = ChatMessage.objects.create(thread=thread,user=to_user,message="Welcome to ChatNest")
        #         chat2.save()

    # Retrieve threads and messages
    if id is not None:
        if thread is not None:
            threads = Thread.objects.filter(pk=thread.pk).prefetch_related('chatmessage_thread').order_by('timestamp')
    chats = (Thread.objects.filter((Q(first_person=request.user.id) & ~Q(second_person=request.user.id)) | (Q(second_person=request.user.id) & ~Q(first_person=request.user.id)))
             .prefetch_related('chatmessage_thread').order_by('timestamp'))
    pic=[]
    for c in chats:
        pp =ProfilePics.objects.filter(Q(user_id=c.first_person) | Q(user_id=c.second_person)).first()
        if pp and pp not in pic:
            pic.append(pp)
    sent_message = request.session.get('sent_message')
    print("cookie", sent_message)
    if sent_message:

        if len(sent_message) > 0:
            chat = ChatMessage.objects.create(thread=thread, user=user, message=sent_message)
            chat.save()
            request.session.pop('sent_message')
            return render(request, 'messages.html',
                          {'id': id, 'Threads': threads, 'to_user': to_user, 'p': prof,
                           'logged_in_user_id': logged_in_user_id, 'chats': chats})
    else:
        if request.method == 'POST':
            msg = request.POST.get('msg')
            request.session['sent_message']=msg
            print(msg)
            return render(request, 'messages.html',
                          {'id': id, 'Threads': threads, 'to_user': to_user, 'p': prof,
                           'logged_in_user_id': logged_in_user_id, 'chats': chats})

    if request.method=="POST":
        if request.POST.get('form_type') == 'form1':
            searchcontent=request.POST.get("searchcontent")
            # searchposts = Posts.objects.filter(Q(brand=searchcontent) | Q(model=searchcontent) | Q(licenseplate=searchcontent))
            request.session['searchposts'] = searchcontent
            return redirect(search)
    return render(request, 'messages.html',
                  {'id': id, 'Threads': threads, 'to_user': to_user,'p':prof, 'logged_in_user_id': logged_in_user_id, 'chats': chats})


# def messages(request,id):
#     user = User.objects.get(id=request.user.id)
#     to_user = None
#     threads = None
#     users = User.objects.filter(is_superuser=0)
#
#     # Combine the friend requests
#     # id = request.GET.get('id')
#     if id is not None:
#         to_user = User.objects.get(id=id)
#         try:
#             # Try to get existing thread between current user and the selected user
#             thread = Thread.objects.get(first_person=user, second_person=to_user)
#         except Thread.DoesNotExist:
#             try:
#                 # Try to get existing thread where the selected user is the first person
#                 thread = Thread.objects.get(first_person=to_user, second_person=user)
#             except Thread.DoesNotExist:
#                 # If no existing thread, create a new thread
#                 thread = Thread.objects.create(first_person=user, second_person=to_user)
#         finally:
#             # Mark all unread messages as read
#             unread_messages = ChatMessage.objects.filter(thread=thread, user=to_user, read=False)
#             for msg in unread_messages:
#                 msg.read = True
#                 msg.save()
#
#     # Retrieve threads and messages
#     if id is not None:
#         if thread is not None:
#             threads = Thread.objects.filter(pk=thread.pk).prefetch_related('chatmessage_thread').order_by('timestamp')
#
#     print(request.user.last_login)
#     return render(request, 'message.html',
#                   {'id': id, 'Threads': threads, 'to_user': to_user})

def like_unlike(request):
    if not request.user.is_authenticated:
        return redirect('login')
    pid = request.GET.get('post_id')
    user_id = request.user.id
    likes = Likes.objects.filter(Q(post_id=pid) & Q(user_id=user_id)).first()
    if likes:
        likes.delete()
    else:
        like = Likes.objects.create(post_id=pid, user_id=user_id)
        like.save()


def post_view(request,id):
    post = Posts.objects.get(id=id)
    comments = Comment.objects.filter(post_id=id)
    context={'post':post,'comments':comments}
    pic = []
    for c in comments:
        pp =ProfilePics.objects.filter(user_id=c.author_id).first()
        if pp and pp not in pic:
            pic.append(pp)
    context['pic'] = pic
    if request.method == "POST":
        if request.POST.get('form_type') == 'form1':
            searchcontent = request.POST.get("searchcontent")
            # searchposts = Posts.objects.filter(Q(brand=searchcontent) | Q(model=searchcontent) | Q(licenseplate=searchcontent))
            request.session['searchposts'] = searchcontent
            return redirect(search)
        elif request.POST.get('form_type') == 'form2':
            if not request.user.is_authenticated:
                return redirect('login')
            comment = request.POST.get('comment')
            pid = request.POST.get('post')
            post = Posts.objects.get(id=pid)
            commented = Comment.objects.create(content=comment, post=post, author=request.user)
            commented.save()
    return render(request,'post_view.html',context)
