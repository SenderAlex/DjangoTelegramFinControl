from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'date']
        widgets = {
                    'amount': forms.NumberInput(attrs={'class': 'form-control'}),
                    'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
                    'type': forms.Select(attrs={'class': 'form-select'}),
                    'category': forms.Select(attrs={'class': 'form-select'}),
                    'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
                }
