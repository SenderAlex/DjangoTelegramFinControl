from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        input_formats=['%Y-%m-%dT%H:%M']  # формат, который отправляет datetime-local
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'type' in self.data:
            try:
                type = self.data['type']
                self.fields['category'].queryset = Category.objects.filter(type=type)  # в выпадающем списке для выбора
                # категорий будут отображаться только те категории, которые соответствуют выбранному типу
                # .queryset — это атрибут, который определяет, какие записи из модели будут доступны для выбора.
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Category queryset
        elif self.instance.pk:  # ?????
            if self.instance and self.instance.category and self.instance.category.type:
                type_instance = self.instance.category.type
                self.fields['category'].queryset = Category.objects.filter(type=type_instance)
            else:
                self.fields['category'].queryset = Category.objects.none()

        else:
            self.fields['category'].queryset = Category.objects.none()  # устанавливает пустой набор данных для поля category


