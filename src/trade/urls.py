"""trade URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from trade.user.urls import user_urls
from trade.resource.urls import resource_urls
from trade.order.urls import order_urls
from trade.mp.urls import mp_urls
from trade.views import HeartBeatView
from trade.debug.views import DebugView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^heartbeat$', HeartBeatView.as_view()),
    url(r'^debug', DebugView.as_view()),
    url(r'^mp', include(mp_urls)),
    url(r'^user', include(user_urls)),
    url(r'^resource', include(resource_urls)),
    url(r'^order', include(order_urls)),
]
