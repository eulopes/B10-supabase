from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'total_points', 'current_balance', 'updated_at')
    list_filter = ('tier',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('total_points', 'current_balance', 'tier')
    actions = ['reset_points']

    @admin.action(description='Zerar pontos/tier (via PointsEngineService)')
    def reset_points(self, request, queryset):
        from apps.loyalty.services import PointsEngineService

        for profile in queryset:
            PointsEngineService.reset(profile.user, reason=f'Reset manual via admin por {request.user}')
        self.message_user(request, f'{queryset.count()} perfil(is) zerado(s).')
