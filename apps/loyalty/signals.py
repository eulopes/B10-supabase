import django.dispatch

# Disparado sempre que o PointsEngineService credita/debita pontos de um
# torcedor. Outros apps (ex: content, para badges de check-in; futuras
# integrações Discord/Twitch) podem se inscrever aqui sem o engine precisar
# conhecê-los — é o ponto de extensão principal do sistema de gamificação.
points_awarded = django.dispatch.Signal()  # kwargs: user, amount, reason, source, profile

tier_changed = django.dispatch.Signal()  # kwargs: user, old_tier, new_tier, profile
