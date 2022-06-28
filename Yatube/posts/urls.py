from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path(
        'group/<slug:slug>/', 
        views.group_posts, 
        name='group_list'
    ),
    path('', views.index, name='index'),
    path(
        'profile/<str:username>/',
        views.profile,
        name='profile'
    ),
    # Просмотр записи
    path(
        'post_detail/<post_id>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'post_create/',
        views.post_create,
        name='post_create'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
    )
]
