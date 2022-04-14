import email
from turtle import update
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Message, Room, Topic,Message,User
from django.db.models import Q
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics,
            'room_count': room_count,
            'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)

def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages = user.message_set.all()
    topics=Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 
               'topics': topics}
    return render(request,'base/user_profile.html',context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by('created')
    participants = room.participants.all()
    update=False
    if request.method=='POST':
        message=Message.objects.create(
            User=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context = {'room': room,'room_messages':room_messages,'participants':participants,'update':update}
    return render(request, 'base/room.html', context)


@login_required(login_url='login-user')
def createRoom(request):
    form = RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic,created =Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
        # if form.is_valid():
        #     room=form.save(commit=False)
        #     room.host=request.user
        #     room.save()
        #     return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, 'base/base_room.html', context)


@login_required(login_url='login-user')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not Allowed Here')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic,created =Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name=request.POST.get('name')
        room.description=request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics ,'room':room}
    return render(request, 'base/base_room.html', context)


@login_required(login_url='login-user')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not Allowed Here')
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete_room_and_delete_message.html', {'obj': room})


def loginUser(request):
    page='login-user'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User Does Not Exist')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'User or Password Does Not Exist')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form=MyUserCreationForm()
    page='register-user'
    if request.method=='POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An Error Occured While Registration')
    context = {'page': page,'form':form}
    return render(request, 'base/login_register.html', context)


@login_required(login_url='login-user')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.User:
        return HttpResponse('You are not Allowed Here')
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete_room_and_delete_message.html', {'obj': message})



@login_required(login_url='login-user')
def updateMessage(request, pk):
    user_message = Message.objects.get(id=pk)
    room=user_message.room
    room_messages = room.message_set.all().order_by('created')
    participants = room.participants.all()
    update=True
    if request.user != user_message.User:
        return HttpResponse('You are not Allowed Here')
    if request.method == 'POST':
        user_message.body = request.POST.get('body')
        room_id= user_message.room.id
        user_message.save()
        return redirect('room',pk=room_id)
    context = {'room': room, 'room_messages': room_messages,
               'update': update, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login-user')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method=='POST':
        form=UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    return render(request,'base/update_user.html',{'form':form})


def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

def activityPage(request):
    room_messages=Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})