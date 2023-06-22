from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(verbose_name="Электронная почта",
                              max_length=254,
                              unique=True,
                              null=False,)
    username = models.CharField(
        max_length=150,
        unique=True,
        null=False)
    first_name = models.CharField(verbose_name="Имя пользователя",
                                  max_length=150,
                                  blank=True)
    last_name = models.CharField(verbose_name="Фамилия пользователя",
                                 max_length=150,
                                 blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.email


class Follow(models.Model):
    """Модель подписчика."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="пользователь",)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="автор",)

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscription",)]
