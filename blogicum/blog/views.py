from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from .forms import UserEditForm, CommentForm, PostForm


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    ordering = '-pub_date'
    paginate_by = 10


class PostListView(PostMixin, generic.ListView):
    template_name = 'blog/index.html'

    def add_count(self, posts):
        for post in posts:
            post.comment_count = post.comments.count()
        return posts

    def get_queryset(self):
        queryset = Post.objects.filter(
            pub_date__date__lt=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related(
            'author',
            'location',
            'category'
        ).prefetch_related(
            'comments'
        ).order_by(self.ordering)

        return self.add_count(queryset)


class CategoryPostsListView(PostListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        # Получаем slug категории из URL
        category_slug = self.kwargs.get('category')

        # Получаем объект категории или вызываем 404,
        # если не найдено или не опубликовано
        self.category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )

        # Фильтруем посты по категории и другим условиям
        queryset = self.category.posts.filter(
            category=self.category,
            pub_date__date__lt=timezone.now(),
            is_published=True,
        ).select_related(
            'author',
            'location',
            'category'
        ).order_by(self.ordering)

        return self.add_count(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем объект категории в контекст для использования в шаблоне
        context['category'] = self.category
        return context


class PostDetailView(PostMixin, generic.DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем комментарии к посту
        context['comments'] = self.object.comments.order_by('created_at')
        context['form'] = CommentForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        # Если пост не опубликован и пользователь не автор, возвращаем 404
        if not post.is_published and (not request.user.is_authenticated
                                      or request.user != post.author):
            raise Http404("Пост не найден.")
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, PostMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        # Автоматически добавляем автора перед сохранением
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        # Если пользователь не авторизован
        if not request.user.is_authenticated:
            # Перенаправляем на страницу публикации
            return HttpResponseRedirect(
                reverse('blog:post_detail',
                        kwargs={'post_id': self.kwargs['post_id']})
            )

        # Проверяем, является ли пользователь автором поста
        post = self.get_object()
        if post.author != request.user:
            # Вместо 403 ошибки перенаправляем на страницу публикации
            return HttpResponseRedirect(
                reverse('blog:post_detail',
                        kwargs={'post_id': self.kwargs['post_id']})
            )

        # Если всё в порядке, продолжаем обработку запроса
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostRequiredMixin,
                     PostCreateView,
                     generic.edit.UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(PostRequiredMixin,
                     PostCreateView,
                     generic.DeleteView):
    pass


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_post(self):
        """Получение поста по переданному ID."""
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def form_valid(self, form):
        """Общая логика обработки формы."""
        form.instance.post = self.get_post()
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Общая логика для перенаправления после успешной операции."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']}
                       ) + '#comments'


class CommentCreateView(CommentMixin, generic.CreateView):
    """Создание комментария."""


class CommentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        # Проверяем, является ли пользователь автором комментария
        сomment = self.get_object()
        if сomment.author != request.user:
            # Вместо 403 ошибки перенаправляем на страницу публикации
            return HttpResponseRedirect(
                reverse('blog:post_detail',
                        kwargs={'post_id': self.kwargs['post_id']})
            )

        # Если всё в порядке, продолжаем обработку запроса
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentRequiredMixin,
                        CommentMixin,
                        generic.UpdateView):
    """Редактирование комментария."""


class CommentDeleteView(CommentRequiredMixin,
                        CommentMixin,
                        generic.DeleteView):
    """Удаление комментария."""


class PostView(generic.View):

    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)


class UserProfilelView(PostListView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['profile'] = get_object_or_404(
            get_user_model(), username=self.kwargs['username']
        )
        return context_data

    def get_queryset(self):
        queryset = Post.objects.filter(
            author__username=self.kwargs['username']
        ).order_by(self.ordering)

        return self.add_count(queryset)


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
