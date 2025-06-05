from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Dispute, Return, Order, DisputeNote
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
import logging
import json

logger = logging.getLogger(__name__)


class DisputeListView(ListView):
    model = Dispute
    template_name = 'disputes/dispute_list.html'
    context_object_name = 'disputes'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_disputes'] = self.get_queryset().count()
        context['returns'] = Return.objects.all().select_related('order')
        return context


class DisputeDetailView(DetailView):
    model = Dispute
    template_name = 'disputes/dispute_detail.html'
    context_object_name = 'dispute'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.notes.all().order_by('-created_at')
        context['tracking_history'] = self.object.tracking_history.all().order_by('-created_at')
        return context


@require_http_methods(["GET"])
def dispute_create_form(request):
    """HTMX endpoint for getting the dispute creation form"""
    logger.info("Dispute create form requested")
    returns = Return.objects.all().select_related('order')
    html = render_to_string(
        'disputes/partials/dispute_form.html',
        {'returns': returns},
        request=request
    )
    return HttpResponse(html)


@require_http_methods(["POST"])
def dispute_create(request):
    """HTMX endpoint for creating a new dispute"""
    logger.info("Dispute create requested with data: %s", request.POST)
    
    try:
        return_id = request.POST.get('return_id')
        reason = request.POST.get('reason')
        priority = request.POST.get('priority', 'medium')
        assigned_to = request.POST.get('assigned_to')
        note = request.POST.get('note')
        file = request.FILES.get('file')
        user = request.POST.get('user')
        
        # Validate all required fields
        if not all([return_id, reason, assigned_to, note, file, user]):
            missing_fields = []
            if not return_id: missing_fields.append('return_id')
            if not reason: missing_fields.append('reason')
            if not assigned_to: missing_fields.append('assigned_to')
            if not note: missing_fields.append('note')
            if not file: missing_fields.append('file')
            if not user: missing_fields.append('user')
            
            logger.error("Missing required fields: %s", ', '.join(missing_fields))
            return HttpResponse(f"Missing required fields: {', '.join(missing_fields)}", status=400)
        
        # Get the return record
        return_record = get_object_or_404(Return, id=return_id)
        
        # Create the dispute
        dispute = Dispute.objects.create(
            linked_return=return_record,
            reason=reason,
            priority=priority,
            status='pending',
            assigned_to=assigned_to
        )
        
        # Create initial note with document
        DisputeNote.objects.create(
            dispute=dispute,
            note=note,
            file=file,
            created_by=user
        )
        
        logger.info("Dispute created successfully: %s", dispute)
        
        # Return the updated list
        disputes = Dispute.objects.all().order_by('-created_at')
        html = render_to_string(
            'disputes/partials/dispute_list_partial.html',
            {'disputes': disputes},
            request=request
        )
        return HttpResponse(html)
        
    except Exception as e:
        logger.error("Error creating dispute: %s", str(e))
        return HttpResponse(f"Error creating dispute: {str(e)}", status=500)


@require_http_methods(["GET"])
def dispute_list_partial(request):
    """HTMX endpoint for updating the dispute list"""
    disputes = Dispute.objects.all().order_by('-created_at')
    html = render_to_string(
        'disputes/partials/dispute_list_partial.html',
        {'disputes': disputes},
        request=request
    )
    return HttpResponse(html)
