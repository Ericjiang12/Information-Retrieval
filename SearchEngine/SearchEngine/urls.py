from django.contrib import admin
from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from search import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='search.html')),
    url(r'^search.html$', TemplateView.as_view(template_name='search.html'), name="search"),
    url(r'^result.html', views.result, name='result'),
    url('admin/', admin.site.urls),
]
