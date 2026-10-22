from typing import ClassVar

from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("title", "text", "city", "photo", "warehouse")
        widgets: ClassVar[dict] = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "warehouse": forms.Select(attrs={"class": "form-select"}),
        }
