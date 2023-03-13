# Third Party Stuff
from rest_framework.routers import DefaultRouter

# email_service
from .views import EmailServiceViewSet

default_router = DefaultRouter(trailing_slash=False)
default_router.register("email", EmailServiceViewSet, basename="email")

urlpatterns = list(default_router.urls)
