from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
from .models import Transaction
from .forms import TransactionForm, TransactionSearchForm

# Create your views here.

def hello_world(request):
    return render(request, "hello_world.html")

def home(request):
    """Home page with calendar and quick stats"""
    recent_transactions = Transaction.objects.all()[:5]
    
    # Get current month and year, or from request
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Calculate previous and next month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        next_month = datetime(year + 1, 1, 1).date()
    else:
        next_month = datetime(year, month + 1, 1).date()
    
    if month == 1:
        prev_month = datetime(year - 1, 12, 1).date()
    else:
        prev_month = datetime(year, month - 1, 1).date()
    
    # Get all transactions for the month
    transactions_this_month = Transaction.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Group transactions by date
    transactions_by_date = defaultdict(list)
    for transaction in transactions_this_month:
        transactions_by_date[transaction.date.day].append(transaction)
    
    # Create calendar data
    cal = calendar.monthcalendar(year, month)
    calendar_data = []
    
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({
                    'day': 0,
                    'transactions': [],
                    'total': 0,
                    'is_today': False
                })
            else:
                day_transactions = transactions_by_date.get(day, [])
                day_total = sum(float(t.amount) for t in day_transactions)
                is_today = (day == today.day and month == today.month and year == today.year)
                
                week_data.append({
                    'day': day,
                    'transactions': day_transactions,
                    'total': day_total,
                    'is_today': is_today
                })
        calendar_data.append(week_data)
    
    # Calculate monthly total
    monthly_total = transactions_this_month.aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, "home.html", {
        'recent_transactions': recent_transactions,
        'calendar_data': calendar_data,
        'current_month': datetime(year, month, 1).strftime('%B %Y'),
        'current_year': year,
        'current_month_num': month,
        'prev_month': prev_month,
        'next_month': next_month,
        'monthly_total': monthly_total,
        'today': today,
    })


class TransactionListView(ListView):
    """List all transactions with search and filter functionality"""
    model = Transaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        
        # Get search parameters
        keyword = self.request.GET.get('keyword', '')
        category = self.request.GET.get('category', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        # Apply filters
        if keyword:
            queryset = queryset.filter(note__icontains=keyword)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TransactionSearchForm(self.request.GET)
        
        # Pass search parameters for pagination
        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')
        context['search_params'] = params.urlencode()
        
        return context


class TransactionDetailView(DetailView):
    """Detail view for a single transaction"""
    model = Transaction
    template_name = 'transaction_detail.html'
    context_object_name = 'transaction'


class TransactionCreateView(CreateView):
    """Create a new transaction"""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Expense added successfully!')
        return super().form_valid(form)


class TransactionUpdateView(UpdateView):
    """Update an existing transaction"""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Expense updated successfully!')
        return super().form_valid(form)


class TransactionDeleteView(DeleteView):
    """Delete a transaction"""
    model = Transaction
    template_name = 'transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Expense deleted successfully!')
        return super().delete(request, *args, **kwargs)