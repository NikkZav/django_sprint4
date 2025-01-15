from django.urls import path
from . import views
from django.views.generic import CreateView, UpdateView


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('category/<slug:category>/',
         views.CategoryPostsListView.as_view(),
         name='category_posts'),

    path('posts/<int:post_id>/',
         views.PostView.as_view(),
         name='post_detail'),

    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),

    path('posts/<int:post_id>/edit/',  # wait work...
         CreateView.as_view(),
         name='edit_post'),

    path('posts/<int:post_id>/delete/',  # wait work...
         CreateView.as_view(),
         name='delete_post'),

    path('posts/<int:post_id>/comment/',  # in work...
         views.PostView.as_view(),
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',  # wait work...
         views.CommentEditView.as_view(),
         name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',  # wait work...
         views.CommentDeleteView.as_view(),
         name='delete_comment'),


    path('profile/edit/',
         views.UserUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<username>/',
         views.UserProfilelView.as_view(),
         name='profile'),
]
