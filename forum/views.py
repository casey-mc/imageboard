from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model



from .models import Board, Thread, Post
from .forms import PostForm, BoardForm

def index(request):
    return render(request, 'forum/index.html', {})

def board(request, board_name):
    board = get_object_or_404(Board, name__iexact=board_name)
    return render(request, 'forum/show_board.html', {'board':board})

def thread(request, board_name, thread_id):
    thread = get_object_or_404(Thread, pk=thread_id)
    thread_json = thread.get_json()
    return render(request, 'forum/show_thread.html', {'thread':thread, 'thread_json':thread_json})

#TODO: This has to be able to return something is the form isn't valid
# https://stackoverflow.com/questions/5871730/how-to-upload-a-file-in-django
@login_required
def thread_reply(request, board_name, thread_id):
    if request.method == 'POST':
        thread = get_object_or_404(Thread, pk=thread_id)
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            newpost = Post(media = request.FILES.get('media', None), text=request.POST['replytext'],thread=thread,
            user=request.user)
            # Signals.py updates other users in channel group on post save.
            newpost.save()
            return JsonResponse({'status': 'Okay'})
        else:
            return JsonResponse(form.errors.as_json(), safe=False)
    else:
        return JsonResponse({'status': 'POST only'})

@login_required
def add_thread(request, board_name):
    board = get_object_or_404(Board, name=board_name)
    t = Thread(title=request.POST['title'], text=request.POST['text'], user=request.user, board=board)
    t.save()
    return HttpResponseRedirect(reverse('forum:show-thread', args=(board_name,t.id,)))

# TODO: Login needs to be required to POST to this, but not to GET it
def create_board(request):
    if request.method == 'GET':
        return render(request, 'forum/create-board.html', {})
    elif request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            cleaned_form = form.cleaned_data
            new_board = Board(
                name=cleaned_form['name'],
                title=cleaned_form['title'],
                description=cleaned_form['description'],
                owner=request.user)
            new_board.save()
            # TODO: Have this redirect to a board admin page
            # return HttpResponseRedirect(reverse('forum:show-board', args=(new_board.name,)))
            return JsonResponse({"location" : reverse('forum:show-board', args=(new_board.name,))})
        else:
            return JsonResponse(form.errors.as_json(), safe=False)
    else:
        return JsonResponse({'status': 'POST only'})

@login_required
def add_moderator(request, board_name, user_id):
    if request.method == 'POST':
        board = get_object_or_404(Board, name=board_name)
        # Only the owner of the board can add moderators, change this later if necessary.
        if board.owner == request.user:
            user = get_object_or_404(get_user_model(), pk=user_id)
            if user not in board.moderators.all():
                board.moderators.add(user)
                return JsonResponse(
                    {'message' : 'User {} is now a moderator of /{}'.format(user.screen_name,board.name)}
                    )
            else:
                return JsonResponse(
                    {'status': 'false', 'message': 'User {} is already a moderator of /{}'.format(user.screen_name,board.name)},
                    # TODO: Is 406 the right code?
                    status=406
                )
    else:
        #TODO: test this
        return HttpResponse("<h1>POST only</h1>",status=405)

@login_required
def delete_post(request, board_name, post_id):
    if request.method == 'DELETE':
        post = get_object_or_404(Post, pk=post_id)
        board = post.thread.board
        is_mod = (board.owner == request.user or request.user in board.moderators.all())
        if post.user == request.user or is_mod:
            post.delete()
            return JsonResponse({'message' : 'Post Successfully Deleted'})
        else:
            return JsonResponse({'message' : 'Not authorized to delete post'},status=403)
    else:
        #TODO: test this
        return HttpResponse("<h1>DELETE only</h1>",status=405)