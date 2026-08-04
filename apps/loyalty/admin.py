from django.contrib import admin

from .models import PointsTransaction, Redemption, RewardItem, TierRule


@admin.register(TierRule)
class TierRuleAdmin(admin.ModelAdmin):
    list_display = ('order', 'code', 'label', 'min_points', 'max_points', 'discount_percent', 'free_shipping')
    ordering = ('order',)


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'source', 'created_at')
    list_filter = ('source',)
    search_fields = ('user__username', 'reason')
    readonly_fields = ('user', 'amount', 'reason', 'source', 'created_at')


@admin.register(RewardItem)
class RewardItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost_points', 'stock', 'active')
    list_filter = ('active',)


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'points_spent', 'created_at')
    readonly_fields = ('user', 'reward', 'points_spent', 'created_at')
