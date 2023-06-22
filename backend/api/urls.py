from django.urls import include, path
from rest_framework import routers

from .views import (IngredientsViewSet, RecipesViewSet, TagsViewSet,
                    UsersViewSet)

app_name = "api"

router = routers.DefaultRouter()
router.register("tags", TagsViewSet, basename="tags")
router.register("users", UsersViewSet, basename="users")
router.register("recipes", RecipesViewSet, basename="recipes")
router.register("ingredients", IngredientsViewSet, basename="ingredients")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
