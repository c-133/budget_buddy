from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Transaction
from .forms import TransactionForm, TransactionSearchForm

# Create your views here.

def hello_world(request):
    return render(request, "hello_world.html")

def home(request):
    """Home page with quick stats"""
    recent_transactions = Transaction.objects.all()[:5]
    return render(request, "home.html", {
        'recent_transactions': recent_transactions
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