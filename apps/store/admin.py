from django.contrib import admin

from .models import Coupon, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_exclusive_tier')
    list_filter = ('is_exclusive_tier',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'active', 'times_used', 'usage_limit')
    list_filter = ('active',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_final', 'points_earned', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]
