from django import forms
from inventory.models import Product, ShippingBox


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "description", "length", "width", "height", "weight", "is_active"]
        widgets = {
            "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. PROD-1001"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional description"}),
            "length": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "cm"}),
            "width": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "cm"}),
            "height": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "cm"}),
            "weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "kg"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ShippingBoxForm(forms.ModelForm):
    class Meta:
        model = ShippingBox
        fields = ["code", "name", "length", "width", "height", "max_weight", "cost", "is_active"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. BOX-M"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Box name"}),
            "length": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Internal length in cm"}),
            "width": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Internal width in cm"}),
            "height": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Internal height in cm"}),
            "max_weight": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Max weight payload in kg"}),
            "cost": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "Packaging material cost"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

