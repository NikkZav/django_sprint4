from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views

# Добавьте новые строчки с импортами классов.
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView

# К импортам из django.urls добавьте импорт функции reverse_lazy
from django.urls import include, path, reverse_lazy

from .views import MyLoginView


urlpatterns = [
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('admin/', admin.site.urls),



    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url='/',
        ),
        name='registration',
    ),
    # Логин.
    path('login/', MyLoginView.as_view(), name='login'),
    # Логаут.
    path('logout/', views.LogoutView.as_view(), name='logout'), 

    # Изменение пароля.
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    # Сообщение об успешном изменении пароля.
    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # Восстановление пароля.
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    # Сообщение об отправке ссылки для восстановления пароля.
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # Вход по ссылке для восстановления пароля.
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # Сообщение об успешном восстановлении пароля.
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# Если проект запущен в режиме разработки...
if settings.DEBUG:
    import debug_toolbar
    # Добавить к списку urlpatterns список адресов из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),) 
