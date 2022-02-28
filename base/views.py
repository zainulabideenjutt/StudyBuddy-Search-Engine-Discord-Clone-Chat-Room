from asyncio.windows_events import NULL
from pydoc_data.topics import topics
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Message, Room, Topic,Message
from django.db.models import Q
from .forms import RoomForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
# Create your views here.

# rooms=[{'id':1,'name':'Learn Python'},
#       {'id':2,'name':'Design with me'},
#       {'id': 3, 'name': 'Frontend Developer'},
#     ]


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
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
    if request.method=='POST':
        message=Message.objects.create(
            User=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    context = {'room': room,'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login-user')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room=form.save(commit=False)
            room.host=request.user
            room.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/base_room.html', context)


@login_required(login_url='login-user')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not Allowed Here')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
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
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User Does Not Exist')
        user = authenticate(request, username=username, password=password)
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
    form=UserCreationForm()
    page='register-user'
    if request.method=='POST':
        form = UserCreationForm(request.POST)
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



# @login_required(login_url='login-user')
# def updateMessage(request, pk):
#     message = Message.objects.get(id=pk)
#     if request.user != message.User:
#         return HttpResponse('You are not Allowed Here')
#     if request.method == 'POST':
#         message.body = request.POST.get('body')
#         return redirect('home')
#     context = {}
#     return render(request, 'base/update_message.html', context)