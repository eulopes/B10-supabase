from django.contrib import admin
from django.utils.html import format_html

from .models import Coupon, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'price', 'stock', 'is_exclusive_tier')
    list_display_links = ('image_preview', 'name')
    list_editable = ('price', 'stock')
    list_filter = ('is_exclusive_tier',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview_large',)
    fields = ('name', 'slug', 'description', 'price', 'stock', 'is_exclusive_tier', 'image_url', 'image_preview_large')

    @admin.display(description='Foto')
    def image_preview(self, obj):
        if not obj.image_url:
            return '—'
        return format_html('<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:6px;">', obj.image_url)

    @admin.display(description='Pré-visualização')
    def image_preview_large(self, obj):
        if not obj.image_url:
            return 'Sem imagem definida ainda.'
        return format_html('<img src="{}" style="max-height:220px;border-radius:8px;">', obj.image_url)


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
