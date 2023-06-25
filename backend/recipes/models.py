from django.db import models
from users.models import User


class Tag(models.Model):
    """Модель для тегов."""

    name = models.CharField(
        verbose_name='название',
        help_text='название тэга',
        max_length=200,
        unique=True)

    color = models.CharField(
        verbose_name='HEX-код',
        help_text='HEX-код для обозначения цвета тэга',
        max_length=7,
        unique=True)

    slug = models.SlugField(
        verbose_name='слаг',
        help_text='имя для URL',
        unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для ингредиентов."""

    name = models.CharField(
        verbose_name='ингредиент',
        help_text='название ингредиента',
        max_length=200)

    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        help_text='единица измерения количества ингредиента',
        max_length=200,)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для рецептов."""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэги',
        help_text='тэги по рецепту',)

    author = models.ForeignKey(
        User,
        verbose_name='автор',
        help_text='автор публикации рецепта',
        on_delete=models.CASCADE,
        related_name='recipes')

    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты',
        help_text='ингредиенты для приготовления по рецепту',
        through='IngredientInRecipesAmount',)
    name = models.CharField('Название рецепта',
                            max_length=200)

    image = models.ImageField('Фотография готового блюда',
                              upload_to='recipes/',)

    text = models.TextField('Описание рецепта')

    cooking_time = models.IntegerField(
        verbose_name='время приготовления',
        help_text='время приготовления блюда',)

    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientInRecipesAmount(models.Model):
    """
    Вспомогательная модель для просмотра количества
    ингредиентов в рецепте.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='рецепт',)

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='ингредиент',)

    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        help_text='необходимое количество данного ингредиента',)

    class Meta:
        verbose_name = 'количество ингредиентов'
        verbose_name_plural = 'количество ингредиентов'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='unique_ingredient',)]


class FavoriteReceipe(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='пользователь')

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='рецепты',)

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'рецепты в избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_recipe',)]


class ShoppingCart(models.Model):
    """Модель для списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='пользователь')

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipes',
        verbose_name='рецепты',)

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='recipe_in_shopping_cart',)]
