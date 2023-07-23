from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from drf_yasg.utils import swagger_auto_schema

from apps.transaction.api.serializer import TransactionSerializer
from apps.transaction.models import Transaction


class TransactionCreateView(CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        tags=['transaction'],
        request_body=TransactionSerializer,
        responses={
            201: 'Successfully created a new transaction.',
            400: 'Bad Request. The provided data is invalid or incomplete.',
            401: 'Unauthorized. Token authentication failed.',
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
