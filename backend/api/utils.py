from datetime import datetime

from django.shortcuts import HttpResponse


def create_shopping_list(user, ingredients):
    today = datetime.today()
    shopping_list = (
        f'Список покупок для: {user.get_full_name()}\n\n'
        f'Дата: {today:%Y-%m-%d}\n\n'
    )
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    shopping_list += f'\n\nFoodgram ({today:%Y})'
    return shopping_list


def export_ingredients(self, request, ingredients):
    user = request.user
    filename = f'{user.username}_shopping_list.txt'
    shopping_list = create_shopping_list(user, ingredients)
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
