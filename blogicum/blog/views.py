from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserEditForm, CommentForm, PostForm


class PostListView(generic.ListView):
    model = Post
    # выполняет запрос queryset = Post.objects.all(),
    # но мы его переопределим:
    queryset = Post.objects.filter(
        pub_date__date__lt=timezone.now(),
        is_published=True,
        category__is_published=True
    ).select_related('author', 'location', 'category'
                     ).prefetch_related('comments')
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = '-pub_date'
    # ...и даже настройки пагинации:
    paginate_by = 10
    template_name = 'blog/index.html'


class CategoryPostsListView(generic.ListView):
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


class PostDetailView(generic.DetailView):
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
        context['form'] = CommentForm
        return context


class PostCreateView(generic.CreateView, LoginRequiredMixin):
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


class CommentCreateView(generic.FormView, LoginRequiredMixin):
    # model = Post
    template_name = 'blog/detail.html'
    form_class = CommentForm

    def form_valid(self, form):
        # Добавление логики для сохранения комментария
        comment = form.save(commit=False)
        comment.post = Post.objects.get(pk=self.kwargs['post_id'])
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Получение поста из переданных параметров
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': post_id}) + '#comments'


class PostView(generic.View):

    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentCreateView.as_view()
        return view(request, *args, **kwargs)


class CommentEditView(generic.DetailView,
                      generic.FormView,
                      LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_initial(self):
        # Получаем объект и заполняем начальные данные формы
        return {'text': self.get_object().text}

    def form_valid(self, form):
        # Получаем объект комментария
        comment = self.get_object()
        # Обновляем только нужные поля
        comment.text = form.cleaned_data['text']  # Пример обновления поля
        # Сохраняем только обновлённое поле
        comment.save(update_fields=['text'])
        return super().form_valid(form)

    def get_success_url(self):
        # Получение поста из переданных параметров
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': post_id}) + '#comments'


class CommentDeleteView(generic.DeleteView, LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        # Получение поста из переданных параметров
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': post_id}) + '#comments'


class UserProfilelView(PostListView):
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
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


class UserUpdateView(generic.UpdateView):
    model = get_user_model()
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.object.username})
