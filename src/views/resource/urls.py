from django.conf.urls import url
from views.resource import views

resource_urls = [
    url(r'^$', views.UserResourceView.as_view()),
]
