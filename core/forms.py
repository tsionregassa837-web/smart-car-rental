from django import forms

from .models import Car


class FleetVehicleForm(forms.ModelForm):

    class Meta:
        model = Car

        fields = [
            "name",
            "model_year",
            "plate_number",
            "price_per_day",
            "total_quantity",
            "fleet_status",
            "maintenance_count",
            "maintenance_reason",
            "image",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Toyota Corolla",
                }
            ),

            "model_year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2025",
                }
            ),

            "plate_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. AA-12345",
                }
            ),

            "price_per_day": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Price per day",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "total_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),

            "fleet_status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "maintenance_count": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),

            "maintenance_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": (
                        "Explain why the vehicle "
                        "is under maintenance..."
                    ),
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_total_quantity(self):

        quantity = self.cleaned_data.get(
            "total_quantity"
        )

        if quantity is None:
            raise forms.ValidationError(
                "Total quantity is required."
            )

        if quantity < 1:
            raise forms.ValidationError(
                "Total quantity must be at least 1."
            )

        return quantity

    def clean_maintenance_count(self):

        maintenance_count = (
            self.cleaned_data.get(
                "maintenance_count"
            )
        )

        if maintenance_count is None:
            maintenance_count = 0

        if maintenance_count < 0:
            raise forms.ValidationError(
                "Maintenance count cannot be negative."
            )

        return maintenance_count

    def clean(self):

        cleaned_data = super().clean()

        total_quantity = (
            cleaned_data.get("total_quantity")
        )

        maintenance_count = (
            cleaned_data.get("maintenance_count")
        )

        fleet_status = (
            cleaned_data.get("fleet_status")
        )

        maintenance_reason = (
            cleaned_data.get("maintenance_reason")
        )

        # ----------------------------------------------------
        # MAINTENANCE COUNT
        # ----------------------------------------------------

        if (
            total_quantity is not None
            and maintenance_count is not None
            and maintenance_count > total_quantity
        ):

            self.add_error(
                "maintenance_count",
                (
                    "Maintenance count cannot be "
                    "greater than total quantity."
                ),
            )

        # ----------------------------------------------------
        # MAINTENANCE REASON
        # ----------------------------------------------------

        if (
            fleet_status == "Maintenance"
            and not maintenance_reason
        ):

            self.add_error(
                "maintenance_reason",
                (
                    "Maintenance reason is required "
                    "when the vehicle is under maintenance."
                ),
            )

        return cleaned_data