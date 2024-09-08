from django import forms
from stripe import Review
from core.models import ProductInquiry

from .models import ProductInquiry

from core.models import ProductReview, ShippingInfo, BillingInfo


class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Write review"})
    )

    class Meta:
        model = ProductReview
        fields = ["review", "rating"]


class ProductInquiryForm(forms.ModelForm):
    class Meta:
        model = ProductInquiry
        fields = ["inquiry"]


class BillingInfoForm(forms.ModelForm):
    class Meta:
        model = BillingInfo
        fields = ['name', 'email', 'phone', 'street_address', 
            'city', 'state', 'postal_code', 'country'
        ]


class ShippingInfoForm(forms.ModelForm):
    class Meta:
        model = ShippingInfo
        fields = ['name', 'email', 'phone', 'street_address', 
            'city', 'state', 'postal_code', 'country'
        ]
  

