from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (FavoriteOrShoppingRecipeSerializer, FollowSerializer,
                          IngredientSerializer, RecipesCreateSerializer,
                          RecipesListSerializer, TagSerializer, UserSerializer)
from .utils import export_ingredients


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_class = IngredientFilter


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=["GET"],
            detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(methods=["POST", "DELETE"], detail=True,)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user.id == author.id:
                raise ValidationError(
                    "Вы не можете подписаться на свой аккаунт")
            else:
                serializer = FollowSerializer(Follow.objects.create(
                    user=request.user, author=author),
                    context={"request": request},)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if Follow.objects.filter(
                user=request.user, author=author
            ).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Автор отсутсвует в списке подписок"},
                    status=status.HTTP_400_BAD_REQUEST,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesListSerializer
        return RecipesCreateSerializer

    def get_queryset(self):
        qs = Recipe.objects.select_related("author").prefetch_related(
            "tags",
            "ingredients",
            "recipe",)
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    FavoriteRecipe.objects.filter(
                        user=self.request.user, recipe=OuterRef("id"))),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=self.request.user, recipe=OuterRef("id"))),)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["POST", "DELETE"], detail=True,
            permission_classes=(IsAuthenticated,),)
    def favorite(self, request, pk):
        recipe_pk = self.kwargs.get("pk")
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request.method == "POST":
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            if FavoriteRecipe.objects.filter(user=self.request.user,
                                             recipe=recipe).exists():
                return Response("Вы уже добавили рецепт в избранное",
                                status=status.HTTP_400_BAD_REQUEST)
            FavoriteRecipe.objects.create(user=self.request.user,
                                          recipe=recipe)
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            favorite_obj = get_object_or_404(FavoriteRecipe,
                                             user=self.request.user,
                                             recipe=recipe)
            if not favorite_obj:
                return Response("Рецепт не был в избранном",
                                status=status.HTTP_400_BAD_REQUEST)
            favorite_obj.delete()
            return Response("Удалено", status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST", "DELETE"], detail=True,)
    def shopping_cart(self, request, pk):
        recipe_pk = self.kwargs.get("pk")
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if request.method == "POST":
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            if ShoppingCart.objects.filter(user=self.request.user,
                                           recipe=recipe).exists():
                return Response('Вы уже добавили рецепт в список покупок',
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
            serializer = FavoriteOrShoppingRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            shopping_cart_obj = get_object_or_404(ShoppingCart,
                                                  user=self.request.user,
                                                  recipe=recipe)
            if not shopping_cart_obj:
                return Response('Рецепт не был в списке покупок',
                                status=status.HTTP_400_BAD_REQUEST)
            shopping_cart_obj.delete()
            return Response('Удалено', status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = AmountIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return export_ingredients(self, request, ingredients)
