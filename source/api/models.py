from django.contrib.auth import get_user_model
from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    description = models.TextField(verbose_name='Description')
    due_date = models.DateTimeField(verbose_name='Due date')
    complete = models.BooleanField(default=False, verbose_name='Complete')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='task', verbose_name='Author')

    def __str__(self):
        return f'{self.title}'
