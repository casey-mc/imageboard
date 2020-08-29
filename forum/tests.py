from django.test import TestCase
from .models import Thread, Board, Post, BannedUser
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .forms import BoardForm
from django.conf import settings
import datetime
from django.utils import timezone
from django.utils.timezone import make_aware
import json
from django.core.exceptions import ObjectDoesNotExist

# # Create your tests here.
# class ThreadModelTests(TestCase):

#     def test_post_count(self):
#         """
#         post_count() returns number of posts in thread
#         """
#         new_thread = Thread()

class BoardFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.client.login(username="jacob", password="top_secret")

    def test_blank_form(self):
        """
        Blank Form should render properly
        """
        response = self.client.get(reverse('forum:create-board'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name")

    def test_board_post(self):
        """
        Form should work with random data. Success returns URL of new board.
        Integration Test.
        """
        response = self.client.post(reverse('forum:create-board'), {
            'name':'atestname',
            'title':'any title',
            'description':'some words'})
        
        response.user = self.user
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('forum:show-board', args=('atestname',)))

    def test_board_post_alphabet_name(self):
        """
        Form should reject numerics and special characters in the name.
        """
        form_data = {
            'name': 'a6b',
            'title': 'test',
            'description': 'test'
        }
        form = BoardForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data = {
            'name': 'a*b',
            'title': 'test',
            'description': 'test'
        }
        form = BoardForm(data=form_data)
        self.assertFalse(form.is_valid())

class AddModeratorViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.client.login(username="jacob", password="top_secret")
        self.board = Board.objects.create(
            name='testboard', title='test', description='test', owner=self.user
        )

    def test_add_moderator(self):
        """
        Basic functionality
        """
        test_user = get_user_model().objects.create_user(
            username="new_mod", email="blank@gmail.com", password="based"
            )
        response = self.client.post(reverse('forum:add-moderator', args=(self.board.name, test_user.id,)))
        self.assertContains(response, "is now a moderator")

    def test_moderator_already_exists(self):
        """
        Form should return error if user is already a moderator.
        """
        test_user = get_user_model().objects.create_user(
            username="new_mod", email="blank@gmail.com", password="based"
            )
        self.board.moderators.add(test_user)
        response = self.client.post(reverse('forum:add-moderator', args=(self.board.name, test_user.id,)))
        self.assertEqual(response.status_code, 406)

class DeletePostViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.client.login(username="jacob", password="top_secret")
        self.board = Board.objects.create(
            name='testboard', title='test', description='test', owner=self.user
        )
        self.thread_owner = get_user_model().objects.create_user(
            username='thread_owner', email='ownsthread@gmail.com', password='top_secret')
        self.thread = Thread.objects.create(
            user = self.thread_owner, board = self.board, title = "test", text = "test"
        )

    def test_delete_post(self):
        """
        Basic functionality of view.
        """
        new_post = Post.objects.create(
            user = self.user, text = "testText", thread = self.thread
        )
        response = self.client.delete(
            reverse("forum:delete-post", args=(self.board.name, self.thread.id, new_post.id,))
            )
        self.assertContains(response, "Post Successfully Deleted")

    def test_delete_not_authorized(self):
        """
        A non-mod who doesn't own the post shouldn't be able to delete it.
        """
        board = Board.objects.create(
            name='testboard2', title='test', description='test', owner=self.thread_owner
        )
        thread = Thread.objects.create(
            user = self.thread_owner, board = board, title = "test", text = "test"
        )
        post = Post.objects.create(
            user = self.thread_owner, text = "testText", thread = thread
        )

        response = self.client.delete(
            reverse("forum:delete-post", args=(board.name, self.thread.id, post.id,))
            )
        self.assertEqual(response.status_code, 403)

class BannedUserModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')

    def test_add_banned_user(self):
        """
        Basic functionality of model
        """
        user_to_ban = get_user_model().objects.create_user(
            username='banme', email='test@gmail.com', password='top_secret'
        )
        board = Board.objects.create(
            name='testboard', title='test', description='test', owner=self.user
        )
        banned = BannedUser.objects.create(user=user_to_ban, board=board,
        ban_expiry=timezone.now() + datetime.timedelta(hours=1))
        banned_users = BannedUser.objects.filter(board=board)
        user_after_ban = BannedUser.objects.get(user=user_to_ban)
        self.assertIn(user_after_ban, banned_users)

    def test_expired_ban(self):
        """
        If a user's ban has expired, they should no longer show up in a banned_users query
        """
        user_to_ban = get_user_model().objects.create_user(
            username='banme', email='test@gmail.com', password='top_secret'
        )
        board = Board.objects.create(
            name='testboard', title='test', description='test', owner=self.user
        )
        ban_time = timezone.now() - datetime.timedelta(hours=1)
        banned = BannedUser.objects.create(user=user_to_ban, board=board,
        ban_expiry=ban_time)
        banned_users = BannedUser.objects.filter(board=board)
        self.assertRaises(BannedUser.DoesNotExist, BannedUser.objects.get, user=user_to_ban)

class BanUserViewTests(TestCase):
    def setUp(self):
        self.board_owner = get_user_model().objects.create_user(
            username='jacob', email='jacob@gmail.com', password='top_secret')
        self.client.login(username="jacob", password="top_secret")
        self.board = Board.objects.create(
            name='testboard', title='test', description='test', owner=self.board_owner
        )
        self.thread_owner = get_user_model().objects.create_user(
            username='thread_owner', email='ownsthread@gmail.com', password='top_secret')
        self.thread = Thread.objects.create(
            user = self.thread_owner, board = self.board, title = "test", text = "test"
        )

    def test_ban_user(self):
        ban_user = get_user_model().objects.create_user(
            username='tim', email='tim@gmail.com', password='top_secret')
        new_post = Post.objects.create(
            user = ban_user, text = "testText", thread = self.thread
        )
        response = self.client.post(
            reverse("forum:board-ban-user", args=(self.board.name, ban_user.id,)),
            )
        self.assertContains(response, "User Banned")

    def test_ban_user_7_days(self):
        ban_user = get_user_model().objects.create_user(
            username='tim', email='tim@gmail.com', password='top_secret')
        new_post = Post.objects.create(
            user = ban_user, text = "testText", thread = self.thread
        )
        response = self.client.post(
            reverse("forum:board-ban-user", args=(self.board.name, ban_user.id,)),
            data={'ban_duration' : datetime.timedelta(days=7)}
            )
        json_response = json.loads(response.content)
        time_from_response = datetime.datetime.fromisoformat(json_response['ban_expiry'].replace('Z', '+00:00'))
        ban_time = timezone.now() + datetime.timedelta(days=7)
        #Zero the seconds and microseconds because it only really matters that they're equal down to the minute
        time_from_response = time_from_response.replace(second=0, microsecond=0)
        ban_time = ban_time.replace(second=0, microsecond=0)
        self.assertEqual(time_from_response, ban_time)

    def test_ban_and_delete_post(self):
        ban_user = get_user_model().objects.create_user(
            username='tim', email='tim@gmail.com', password='top_secret')
        new_post = Post.objects.create(
            user = ban_user, text = "testText", thread = self.thread
        )
        response = self.client.post(
            reverse("forum:board-ban-user", args=(self.board.name, ban_user.id,)),
            data = {'post_id' : new_post.id}
            )
        self.assertRaises(Post.DoesNotExist, Post.objects.get, pk=new_post.id)