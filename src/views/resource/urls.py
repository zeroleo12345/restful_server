from django.urls import path
from views.resource import views

resource_urls = [
    path(r'', views.UserResourceView.as_view()),
]
