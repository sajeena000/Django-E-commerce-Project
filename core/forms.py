from django import forms
from stripe import Review

from core.models import ProductReview


class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Write review"})
    )

    class Meta:
        model = ProductReview
        fields = ["review", "rating"]


# Inquiry form
from django import forms

from core.models import ProductInquiry

from .models import ProductInquiry


class ProductInquiryForm(forms.ModelForm):
    class Meta:
        model = ProductInquiry
        fields = ["inquiry"]




