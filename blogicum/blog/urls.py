from django.urls import path
from . import views
from django.views.generic import CreateView, UpdateView


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),

    path('posts/<int:post_id>/',
         views.PostDetailPage.as_view(),
         name='post_detail'
         ),

    path('category/<slug:category>/',
         views.CategoryPostsListView.as_view(),
         name='category_posts'
         ),

    path('profile/edit/', views.UserUpdateView.as_view(), name='edit_profile'),

    path('profile/<username>/',
         views.UserProfilelView.as_view(),
         name='profile',
         ),

    path('posts/create/', CreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', CreateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/', CreateView.as_view(), name='delete_post'),

    path('posts/<int:post_id>/add_comment/', CreateView.as_view(), name='add_comment'),
]
