from django.urls import path

from . import views

app_name = 'forum'
urlpatterns = [
    path('', views.index, name='index'),
    path('boards/create', views.create_board, name="create-board"),
    path('<board_name>/', views.board, name="show-board"),
    path('<board_name>/add-thread', views.add_thread, name="add-thread"),
    path('<board_name>/<int:thread_id>/', views.thread, name="show-thread"),
    path('<board_name>/<int:thread_id>/reply', views.thread_reply, name="thread-reply")
]

