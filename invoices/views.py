from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from .models import Invoice, Payment
from orders.models import Order
from django import forms
from django.http import JsonResponse
import json
import io
from django.template.loader import get_template
from xhtml2pdf import pisa

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference', 'notes', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop('invoice', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        if self.invoice:
            remaining = self.invoice.total_amount - self.invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
            self.fields['amount'].initial = remaining

@login_required
def invoices_list(request):
    invoices = Invoice.objects.all().order_by('-issue_date')
    
    context = {
        'page_obj': invoices,
        'invoice_statuses': Invoice.InvoiceStatus.choices,
        'title': 'Invoices List'
    }
    
    return render(request, 'invoices/invoices_list.html', context)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = invoice.payments.all().order_by('-payment_date')
    
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    remaining = invoice.total_amount - total_paid
    
    context = {
        'invoice': invoice,
        'payments': payments,
        'order_items': invoice.order.items.all(),
        'total_paid': total_paid,
        'remaining': remaining,
        'title': f'Invoice #{invoice.invoice_number}'
    }
    
    return render(request, 'invoices/invoice_detail.html', context)

@login_required
def invoice_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if invoice already exists
    if hasattr(order, 'invoice'):
        messages.error(request, f'Invoice already exists for Order #{order.order_number}')
        return redirect('order-detail', pk=order.pk)
    
    if request.method == 'POST':
        tax_rate = float(request.POST.get('tax_rate', 0))
        discount = float(request.POST.get('discount', 0))
        notes = request.POST.get('notes', '')
        
        invoice = Invoice.objects.create(
            order=order,
            tax_rate=tax_rate,
            discount=discount,
            notes=notes,
            created_by=request.user
        )
        
        messages.success(request, f'Invoice #{invoice.invoice_number} has been created successfully.')
        return redirect('invoice-detail', pk=invoice.pk)
    
    context = {
        'order': order,
        'title': f'Create Invoice for Order #{order.order_number}'
    }
    
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Calculate remaining amount
    total_paid = invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
    remaining = invoice.total_amount - total_paid
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, invoice=invoice)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.created_by = request.user
            
            # Check if payment amount exceeds remaining
            if payment.amount > remaining:
                messages.error(request, f'Payment amount exceeds remaining balance (${remaining}).')
                return redirect('add-payment', pk=invoice.pk)
            
            payment.save()
            
            messages.success(request, f'Payment of ${payment.amount} has been recorded successfully.')
            return redirect('invoice-detail', pk=invoice.pk)
    else:
        form = PaymentForm(invoice=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
        'remaining': remaining,
        'title': f'Add Payment to Invoice #{invoice.invoice_number}'
    }
    
    return render(request, 'invoices/payment_form.html', context)

@login_required
def generate_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Get data for PDF
    context = {
        'invoice': invoice,
        'order_items': invoice.order.items.all(),
        'payments': invoice.payments.all(),
        'total_paid': invoice.payments.aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Render HTML template
    template = get_template('invoices/invoice_pdf.html')
    html = template.render(context)
    
    # Create PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
        return response
    
    return HttpResponse('Error generating PDF', status=400)