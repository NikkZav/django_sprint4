from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, TemplateView, DetailView, UpdateView
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from .forms import UserEditForm, CommentCreateForm, PostForm


class PostListView(ListView):
    model = Post
    # выполняет запрос queryset = Post.objects.all(),
    # но мы его переопределим:
    queryset = Post.objects.filter(
        pub_date__date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related('author', 'location', 'category')
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = '-pub_date'
    # ...и даже настройки пагинации:
    paginate_by = 10
    template_name = 'blog/index.html'


class CategoryPostsListView(ListView):
    model = Post
    ordering = '-pub_date'
    template_name = 'blog/category.html'
    paginate_by = 10

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
        ).select_related('author', 'location', 'category')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем объект категории в контекст для использования в шаблоне
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        # Ограничиваем выборку только опубликованными постами
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем комментарии к посту
        context['comments'] = self.object.comments.order_by('-created_at')
        context['form'] = CommentCreateForm
        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        # Автоматически добавляем автора перед сохранением
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


def add_comment(request):
    form = 


class UserProfilelView(PostListView):
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # print('---\tsuper().get_context_data(**kwargs)\t---')
        # print(super().get_context_data(**kwargs))
        context_data = super().get_context_data(**kwargs)
        context_data['profile'] = get_object_or_404(
            get_user_model(), username=self.kwargs['username']
        )
        return context_data

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            author=self.request.user
        )
        return queryset


class UserUpdateView(UpdateView):
    model = get_user_model()
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
