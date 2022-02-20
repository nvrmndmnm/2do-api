from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from django.utils import timezone
from datetime import timedelta
from todo import settings
from .models import Task
import json


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)
    clocked = ClockedSchedule.objects.create(clocked_time=timezone.now() + timedelta(seconds=5))
    PeriodicTask.objects.create(task='send_email',
                                name=f'password reset email at {timezone.now()}',
                                one_off=True,
                                clocked=clocked,
                                args=json.dumps([
                                    f'Password reset for 2do',
                                    email_plaintext_message,
                                    settings.EMAIL_HOST_USER,
                                    reset_password_token.user.email
                                ])
                                )


@receiver(pre_save, sender=Task)
def status_email_send(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        pass
    else:
        if not obj.complete == instance.complete:
            clocked = ClockedSchedule.objects.create(clocked_time=timezone.now() + timedelta(seconds=5))
            PeriodicTask.objects.create(task='send_email',
                                        name=f'todo-task status change at {timezone.now()}',
                                        one_off=True,
                                        clocked=clocked,
                                        args=json.dumps([
                                            f'Task status updated',
                                            f'Task status changed to {instance.complete}',
                                            settings.EMAIL_HOST_USER,
                                            obj.author.email
                                        ])
                                        )
