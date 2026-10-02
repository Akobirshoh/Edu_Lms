from django import forms

from accounts.models import StudentProfile
from coins.models import CoinTransaction, ShopItem


class ShopItemForm(forms.ModelForm):
    class Meta:
        model = ShopItem
        fields = ['name', 'image', 'price', 'stock', 'is_active']


class ManualCoinForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.select_related('user').all(),
        label="O'quvchi",
    )
    amount = forms.IntegerField(label='Miqdor')
    comment = forms.CharField(max_length=255, required=False, label='Izoh')

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount == 0:
            raise forms.ValidationError("Miqdor 0 bo'lishi mumkin emas.")
        return amount
