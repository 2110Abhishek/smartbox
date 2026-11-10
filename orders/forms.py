from django import forms
from django.forms import inlineformset_factory
from orders.models import Order, OrderItem
from inventory.models import Product


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["order_number", "customer_name", "customer_email"]
        widgets = {
            "order_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. ORD-1001"}),
            "customer_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Customer Full Name"}),
            "customer_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "customer@example.com"}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1", "value": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active products should be selectable for new items
        self.fields["product"].queryset = Product.objects.filter(is_active=True)


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)

