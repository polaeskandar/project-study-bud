from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist!")

        user = authenticate(request, email=email, password=password)

        if user != None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Wrong password or username!")

    context = {"page": "login"}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    context = {"form": MyUserCreationForm}

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration!")

    return render(request, "base/login_register.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    rooms_count = rooms.count()
    topics = Topic.objects.all()[:5]
    rooms_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        "rooms_count": rooms_count,
        "rooms_messages": rooms_messages,
    }

    return render(
        request,
        "base/home.html",
        context,
    )


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )

        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants,
    }
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    rooms_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "rooms_messages": rooms_messages,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )

        room.participants.add(request.user)
        return redirect("home")

    topics = Topic.objects.all()
    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("Unauthorized!")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")

    topics = Topic.objects.all()
    context = {"form": form, "topics": topics, "room": room}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Unauthorized!")

    if request.method == "POST":
        room.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Unauthorized!")

    if request.method == "POST":
        message.delete()
        return redirect("home")

    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            return redirect("profile", pk=user.id)

    return render(request, "base/update_user.html", {"form": form})


def browseTopics(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""

    topics = Topic.objects.filter(Q(name__icontains=q))[:5]

    return render(request, "base/topics.html", {"topics": topics})
