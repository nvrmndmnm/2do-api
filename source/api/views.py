from django.contrib.auth import user_logged_in
from django.utils import timezone
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.models import Task
from api.serializers import TaskSerializer, TaskListSerializer, TaskCreateSerializer, LoginSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in "list":
            return TaskListSerializer
        if self.action in 'create':
            return TaskCreateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["POST"], url_path="execute", url_name="execute")
    def execute_task(self, request, *args, **kwargs):
        task_pk = kwargs["pk"]
        task = get_object_or_404(Task, pk=task_pk)
        if not task.complete:
            task.complete = True
            task.save()
            return Response({'detail': f'Task [{task.title}] marked complete'}, status=status.HTTP_200_OK)
        return Response({'detail': f'Task [{task.title}] already marked complete'}, status=status.HTTP_200_OK)


class LoginView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(user, token_ttl)
        user_logged_in.send(sender=user.__class__,
                            request=request, user=user)
        data = self.get_post_response_data(request, token, instance)
        return Response(data)
