from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

RED = "#FF0000"
GREEN = "#008000"
BLUE = "#0000FF"

CHOICES = ((RED, "красный"), (GREEN, "зелёный"), (BLUE, "голубой"))


class Tag(models.Model):
    """Модель тэга."""

    name = models.CharField(verbose_name="тэг", max_length=200, unique=True)
    color = models.CharField(verbose_name="цвет тэга",
                             max_length=7,
                             choices=CHOICES,
                             unique=True)
    slug = models.SlugField(verbose_name="slug тэга",
                            max_length=200,
                            unique=True)

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "тэги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(verbose_name="название", max_length=200)
    measurement_unit = models.CharField(verbose_name="единица измерения",
                                        max_length=200)

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="recipe",
                               verbose_name="автор",)
    name = models.CharField(verbose_name="название рецепта", max_length=200)
    image = models.ImageField(verbose_name="фото блюда",
                              upload_to="media/recipes/")
    text = models.TextField(verbose_name="текстовое описание")
    ingredients = models.ManyToManyField(Ingredient,
                                         through="AmountIngredient",
                                         verbose_name="ингредиенты")
    tags = models.ManyToManyField(Tag,
                                  related_name="recipe",
                                  verbose_name="тэги")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="время приготовления в минутах",
        validators=[MinValueValidator(
            1, "Ой, время приготовления не может быть меньше 1 минуты")],)
    pub_date = models.DateTimeField(
        verbose_name="дата публикации рецепта", auto_now_add=True)

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    """Модель количества ингредиента."""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="recipe",
                               verbose_name="рецепт",)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name="ingredient",
                                   verbose_name="ингредиент",)
    amount = models.PositiveSmallIntegerField(
        verbose_name="количество",
        validators=[MinValueValidator(
            1, "Ой, ингредиентов не может быть меньше 1")],)

    class Meta:
        verbose_name = "количество ингредиента"
        verbose_name_plural = "количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_ingredient",)]


class FavoriteRecipe(models.Model):
    """Модель избранного рецепта."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="favorite_user",
                             verbose_name="пользователь",)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="favorite_recipe",
                               verbose_name="рецепт",)

    class Meta:
        verbose_name = "количество ингредиента"
        verbose_name_plural = "количество ингредиентов"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite_recipe",)]


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="shopping_cart_user",
                             verbose_name="пользователь",)
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="shopping_cart_recipe",
                               verbose_name="рецепт",)

    class Meta:
        verbose_name = "список покупок"
        verbose_name_plural = "списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_recipe_in_shopping_cart",)]
