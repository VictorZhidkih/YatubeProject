from django.db import models


class CreatedModels(models.Model):
    """Абстракная модель.Добавляет дату создания"""
    created = models.DateField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
