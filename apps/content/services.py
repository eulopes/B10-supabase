from django.db import transaction

from apps.loyalty.models import PointsTransaction
from apps.loyalty.services import PointsEngineService

from .models import CheckIn, Event


class AlreadyCheckedInError(Exception):
    pass


class CheckInService:
    """Caso de uso de check-in: registra a presença e credita pontos via o
    engine de fidelidade (nunca soma pontos direto no perfil)."""

    @staticmethod
    @transaction.atomic
    def check_in(user, event: Event) -> CheckIn:
        if CheckIn.objects.filter(user=user, event=event).exists():
            raise AlreadyCheckedInError(f'Você já fez check-in em "{event.title}".')

        checkin = CheckIn.objects.create(user=user, event=event)

        if event.points_reward > 0:
            PointsEngineService.award_points(
                user, event.points_reward, reason=f'Check-in: {event.title}',
                source=PointsTransaction.Source.EVENT_CHECKIN,
            )
        return checkin
