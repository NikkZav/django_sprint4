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


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.custom_500'

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

    path('auth/login/', MyLoginView.as_view(), name='login'),

    path('auth/', include('django.contrib.auth.urls')),
]

# Если проект запущен в режиме разработки...
if settings.DEBUG:
    import debug_toolbar
    # Добавить к списку urlpatterns список адресов из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),) 
