from django.conf.urls import url
from .views import UserView

urlpatterns = [
    url(r'^$', UserView.as_view()),
]
