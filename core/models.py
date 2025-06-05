from django.db import models
from django.utils import timezone


class Order(models.Model):
    order_id = models.CharField(max_length=30, primary_key=True)
    item_name = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    order_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_id

class Return(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return for {self.order.order_id}"

    def add_tracking_number(self, tracking_number, user=''):
        """Add a tracking number to the return"""
        return Tracking.track_return(
            self,
            'status_changed',
            f'Tracking number added: {tracking_number}',
            user
        )

class Dispute(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('additional_info', 'Additional Info Required'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated')
    ]

    RESOLUTION_CHOICES = [
        ('refund', 'Refund Issued'),
        ('replacement', 'Replacement Sent'),
        ('partial_refund', 'Partial Refund'),
        ('no_action', 'No Action Required'),
        ('other', 'Other')
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ]

    linked_return = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='disputes')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    resolution_type = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    resolution_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    assigned_to = models.CharField(max_length=100, blank=True, help_text='Staff member assigned to handle the dispute')
    customer_notes = models.TextField(blank=True, help_text='Additional notes from the customer')
    internal_notes = models.TextField(blank=True, help_text='Internal notes for staff')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True, help_text='Target resolution date')

    class Meta:
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"Dispute for {self.linked_return.order.order_id}"

    def resolve(self, resolution_type, resolution_notes='', resolution_amount=None, user=''):
        """Resolve the dispute with the given resolution details"""
        self.status = 'resolved'
        self.resolution_type = resolution_type
        self.resolution_notes = resolution_notes
        self.resolution_amount = resolution_amount
        self.resolved_at = timezone.now()
        self.save()
        
        # Create tracking record for resolution
        Tracking.track_dispute(
            self,
            'resolved',
            f'Dispute resolved with {resolution_type}',
            user,
            resolution_amount=resolution_amount
        )

    def escalate(self, reason, user=''):
        """Escalate the dispute with a reason"""
        self.status = 'escalated'
        self.internal_notes += f"\nEscalated: {reason}"
        self.save()
        
        Tracking.track_dispute(
            self,
            'escalated',
            f'Dispute escalated: {reason}',
            user
        )

    def request_info(self, info_needed, user=''):
        """Request additional information from customer"""
        self.status = 'additional_info'
        self.customer_notes += f"\nInfo requested: {info_needed}"
        self.save()
        
        Tracking.track_dispute(
            self,
            'additional_info',
            f'Additional info requested: {info_needed}',
            user
        )

    def assign(self, staff_member, user=''):
        """Assign dispute to a staff member"""
        self.assigned_to = staff_member
        self.save()
        
        Tracking.track_dispute(
            self,
            'under_review',
            f'Assigned to {staff_member}',
            user
        )

    @property
    def is_overdue(self):
        """Check if dispute resolution is overdue"""
        if self.due_date and self.status not in ['resolved', 'rejected']:
            return timezone.now() > self.due_date
        return False

    @property
    def days_open(self):
        """Calculate number of days the dispute has been open"""
        return (timezone.now() - self.created_at).days

class DisputeNote(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    file = models.FileField(upload_to='dispute_attachments/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, help_text='User who created the note')

    def __str__(self):
        return f"Note for {self.dispute.linked_return.order.order_id}"          

class Tracking(models.Model):
    ENTITY_TYPES = [
        ('order', 'Order'),
        ('return', 'Return'),
        ('dispute', 'Dispute')
    ]

    ORDER_STATUS_CHOICES = [
        ('created', 'Order Created'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded')
    ]

    RETURN_STATUS_CHOICES = [
        ('requested', 'Return Requested'),
        ('approved', 'Return Approved'),
        ('label_created', 'Return Label Created'),
        ('in_transit', 'Return In Transit'),
        ('received', 'Return Received'),
        ('processed', 'Return Processed'),
        ('refunded', 'Refund Issued'),
        ('rejected', 'Return Rejected')
    ]

    DISPUTE_STATUS_CHOICES = [
        ('opened', 'Dispute Opened'),
        ('under_review', 'Under Review'),
        ('additional_info', 'Additional Info Requested'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated')
    ]

    entity_type = models.CharField(max_length=10, choices=ENTITY_TYPES)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history', null=True, blank=True)
    return_record = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='tracking_history', null=True, blank=True)
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name='tracking_history', null=True, blank=True)
    status = models.CharField(max_length=20)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=100, blank=True, help_text='User')
    additional_data = models.JSONField(null=True, blank=True, help_text='Additional tracking data')

    class Meta:
        verbose_name_plural = 'Tracking'
        ordering = ['-created_at']

    def __str__(self):
        entity_id = self.order.order_id if self.order else self.return_record.order.order_id if self.return_record else self.dispute.linked_return.order.order_id
        return f"{self.entity_type.title()} {entity_id} - {self.status}"

    @classmethod
    def get_order_tracking(cls, order_id):
        """Get all tracking records for a specific order ID"""
        return cls.objects.filter(
            models.Q(order__order_id=order_id) |
            models.Q(return_record__order__order_id=order_id) |
            models.Q(dispute__linked_return__order__order_id=order_id)
        ).order_by('-created_at')

    @classmethod
    def track_order(cls, order, status, description='', user='', **kwargs):
        """
        Track or update order status
        """
        if status not in dict(cls.ORDER_STATUS_CHOICES):
            raise ValueError(f"Invalid order status. Must be one of: {dict(cls.ORDER_STATUS_CHOICES)}")
        
        tracking, created = cls.objects.update_or_create(
            entity_type='order',
            order=order,
            defaults={
                'status': status,
                'description': description,
                'user': user,
                'additional_data': kwargs if kwargs else None
            }
        )
        return tracking

    @classmethod
    def track_return(cls, return_record, status, description='', user='', **kwargs):
        """
        Track or update return status
        """
        if status not in dict(cls.RETURN_STATUS_CHOICES):
            raise ValueError(f"Invalid return status. Must be one of: {dict(cls.RETURN_STATUS_CHOICES)}")
        
        tracking, created = cls.objects.update_or_create(
            entity_type='return',
            return_record=return_record,
            defaults={
                'status': status,
                'description': description,
                'user': user,
                'additional_data': kwargs if kwargs else None
            }
        )
        return tracking

    @classmethod
    def track_dispute(cls, dispute, status, description='', user='', **kwargs):
        """
        Track or update dispute status
        """
        if status not in dict(cls.DISPUTE_STATUS_CHOICES):
            raise ValueError(f"Invalid dispute status. Must be one of: {dict(cls.DISPUTE_STATUS_CHOICES)}")
        
        tracking, created = cls.objects.update_or_create(
            entity_type='dispute',
            dispute=dispute,
            defaults={
                'status': status,
                'description': description,
                'user': user,
                'additional_data': kwargs if kwargs else None
            }
        )
        return tracking

    def update_status(self, status, description='', user='', **kwargs):
        """
        Update status and additional data for an existing tracking record
        """
        if self.entity_type == 'order' and status not in dict(self.ORDER_STATUS_CHOICES):
            raise ValueError(f"Invalid order status. Must be one of: {dict(self.ORDER_STATUS_CHOICES)}")
        elif self.entity_type == 'return' and status not in dict(self.RETURN_STATUS_CHOICES):
            raise ValueError(f"Invalid return status. Must be one of: {dict(self.RETURN_STATUS_CHOICES)}")
        elif self.entity_type == 'dispute' and status not in dict(self.DISPUTE_STATUS_CHOICES):
            raise ValueError(f"Invalid dispute status. Must be one of: {dict(self.DISPUTE_STATUS_CHOICES)}")

        self.status = status
        self.description = description
        self.user = user
        if kwargs:
            current_data = self.additional_data or {}
            current_data.update(kwargs)
            self.additional_data = current_data
        self.save()
        return self
        
    
        
