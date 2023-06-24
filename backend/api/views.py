from django.db.models import Sum
from django.db.models.expressions import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipesCreateSerializer, RecipesListSerializer,
                          TagSerializer, UserSerializer)


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
        author = self.get_object()
        current_user = self.request.user
        if request.method == "DELETE":
            instance = get_object_or_404(
                Follow, user=current_user, author=author
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=current_user, author=author)
        headers = self.get_success_headers(serializer.data)
        instance_serializer = FollowSerializer(author,
                                               context={'request': request})
        return Response(instance_serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)


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
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(user=request.user,
                                             recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже добавлен в Избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, pk=pk)
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            serializer = RecipesListSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if FavoriteRecipe.objects.filter(user=request.user,
                                         recipe__id=pk).exists():
            FavoriteRecipe.objects.filter(user=request.user,
                                          recipe__id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт не добавлен в Избранное'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST", "DELETE"], detail=True,)
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже добавлен в корзину.'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, pk=pk)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipesListSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe__id=pk).exists():
            ShoppingCart.objects.filter(user=request.user,
                                        recipe__id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт не добавлен в корзину'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        name_ingredient = "recipe__ingredients__ingredient__name"
        meas_unit = "recipe__ingredients__ingredient__measurement_unit"
        amount = "recipe__ingredients__amount"
        grocery_list = (user.shoppingcart.order_by(name_ingredient).values(
            name_ingredient,
            meas_unit,)).annotate(amount_total=Sum(amount))
        count = 0
        arr = f'Список покупок для {user.get_full_name()} \n\n'
        for prod in grocery_list:
            count += 1
            arr += (
                f'№ {count}  '
                f'{prod[name_ingredient]}-'
                f'{prod[meas_unit]}'
                f' {prod["amount_total"]}\n\n'
            )
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(arr, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
