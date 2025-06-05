from django.contrib import admin
from .models import Order, Return, Dispute, DisputeNote, Tracking

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'item_name', 'customer_name', 'customer_email', 'order_date', 'created_at')
    search_fields = ('order_id', 'item_name', 'customer_name', 'customer_email')
    list_filter = ('order_date', 'created_at')
    ordering = ('-order_date',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ('order', 'reason', 'created_at')
    search_fields = ('order__order_id', 'reason')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('linked_return', 'status', 'priority', 'assigned_to', 'created_at', 'resolved_at')
    list_filter = ('status', 'priority', 'created_at', 'resolved_at')
    search_fields = ('linked_return__order__order_id', 'reason', 'assigned_to')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'resolved_at')

@admin.register(DisputeNote)
class DisputeNoteAdmin(admin.ModelAdmin):
    list_display = ('dispute', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('dispute__linked_return__order__order_id', 'note', 'created_by')
    ordering = ('-created_at',)

@admin.register(Tracking)
class TrackingAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'status', 'description', 'user', 'created_at')
    list_filter = ('entity_type', 'status', 'created_at')
    search_fields = ('description', 'user')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
