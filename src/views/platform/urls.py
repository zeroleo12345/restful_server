from django.urls import path
from . import views

platform_urls = [
    path(r'/<int:platform_id>', views.PlatformView.as_view()),
]
