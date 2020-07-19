from django.test import TestCase
from .models import Thread, Board, Post
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User
from .forms import BoardForm

# # Create your tests here.
# class ThreadModelTests(TestCase):

#     def test_post_count(self):
#         """
#         post_count() returns number of posts in thread
#         """
#         new_thread = Thread()

class BoardFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
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