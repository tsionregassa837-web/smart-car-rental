from django import forms

from .models import Car, ExtraCharge, RentalInspection


class FleetVehicleForm(forms.ModelForm):
    """
    Form used by staff to add and edit fleet vehicles.

    This form matches the actual Car model and includes:
    - Basic vehicle information
    - Customer-facing vehicle specifications
    - Fleet management information
    - Maintenance information
    """

    class Meta:
        model = Car

        fields = [
            # ------------------------------------------------
            # BASIC VEHICLE INFORMATION
            # ------------------------------------------------
            "name",
            "model_year",
            "image",
            "price_per_day",

            # ------------------------------------------------
            # VEHICLE SPECIFICATIONS
            # ------------------------------------------------
            "transmission",
            "fuel_type",
            "seats",
            "doors",
            "luggage_capacity",
            "air_conditioning",
            "features",

            # ------------------------------------------------
            # FLEET MANAGEMENT
            # ------------------------------------------------
            "plate_number",
            "total_quantity",
            "fleet_status",

            # ------------------------------------------------
            # MAINTENANCE INFORMATION
            # ------------------------------------------------
            "maintenance_count",
            "maintenance_reason",
        ]

        widgets = {

            # =================================================
            # BASIC VEHICLE INFORMATION
            # =================================================

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
                    "min": "1900",
                }
            ),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),

            "price_per_day": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2500.00",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            # =================================================
            # VEHICLE SPECIFICATIONS
            # =================================================

            "transmission": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "fuel_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "seats": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 5",
                    "min": "1",
                    "max": "100",
                }
            ),

            "doors": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 4",
                    "min": "1",
                    "max": "20",
                }
            ),

            "luggage_capacity": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "air_conditioning": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),

            "features": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Example: Bluetooth, USB, Rear Camera, "
                        "Cruise Control"
                    ),
                }
            ),

            # =================================================
            # FLEET MANAGEMENT
            # =================================================

            "plate_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. AA-12345",
                }
            ),

            "total_quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "e.g. 5",
                }
            ),

            "fleet_status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            # =================================================
            # MAINTENANCE INFORMATION
            # =================================================

            "maintenance_count": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "e.g. 0",
                }
            ),

            "maintenance_reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Example: Scheduled service, engine repair, "
                        "accident repair or inspection."
                    ),
                }
            ),
        }

        labels = {
            # Basic
            "name": "Vehicle Name",
            "model_year": "Model Year",
            "image": "Vehicle Image",
            "price_per_day": "Price Per Day",

            # Specifications
            "transmission": "Transmission",
            "fuel_type": "Fuel Type",
            "seats": "Seats",
            "doors": "Doors",
            "luggage_capacity": "Luggage Capacity",
            "air_conditioning": "Air Conditioning",
            "features": "Features",

            # Fleet
            "plate_number": "Plate Number",
            "total_quantity": "Total Quantity",
            "fleet_status": "Fleet Status",

            # Maintenance
            "maintenance_count": "Maintenance Count",
            "maintenance_reason": "Maintenance Reason",
        }

        help_texts = {
            "name": "Customer-facing vehicle name.",
            "model_year": "Manufacturing/model year of the vehicle.",
            "price_per_day": "Daily rental price charged to customers.",
            "transmission": "Select the vehicle transmission type.",
            "fuel_type": "Select the fuel or power type.",
            "seats": "Number of passenger seats.",
            "doors": "Number of vehicle doors.",
            "luggage_capacity": (
                "Select the vehicle's luggage capacity."
            ),
            "features": (
                "Enter customer-visible features separated by commas."
            ),
            "plate_number": (
                "Vehicle registration or license plate number."
            ),
            "total_quantity": (
                "Total number of units in this vehicle fleet group."
            ),
            "fleet_status": (
                "Current operational status of this fleet."
            ),
            "maintenance_count": (
                "Number of units currently under maintenance."
            ),
            "maintenance_reason": (
                "Required when the fleet is under maintenance."
            ),
        }

    # =========================================================
    # TOTAL QUANTITY VALIDATION
    # =========================================================

    def clean_total_quantity(self):
        quantity = self.cleaned_data.get("total_quantity")

        if quantity is None:
            raise forms.ValidationError(
                "Total quantity is required."
            )

        if quantity < 1:
            raise forms.ValidationError(
                "Total quantity must be at least 1."
            )

        return quantity

    # =========================================================
    # MODEL YEAR VALIDATION
    # =========================================================

    def clean_model_year(self):
        model_year = self.cleaned_data.get("model_year")

        if model_year is None:
            raise forms.ValidationError(
                "Model year is required."
            )

        if model_year < 1900:
            raise forms.ValidationError(
                "Please enter a valid model year."
            )

        return model_year

    # =========================================================
    # PRICE VALIDATION
    # =========================================================

    def clean_price_per_day(self):
        price = self.cleaned_data.get("price_per_day")

        if price is None:
            raise forms.ValidationError(
                "Price per day is required."
            )

        if price < 0:
            raise forms.ValidationError(
                "Price per day cannot be negative."
            )

        return price

    # =========================================================
    # SEATS VALIDATION
    # =========================================================

    def clean_seats(self):
        seats = self.cleaned_data.get("seats")

        if seats is None:
            raise forms.ValidationError(
                "Number of seats is required."
            )

        if seats < 1:
            raise forms.ValidationError(
                "Seats must be at least 1."
            )

        return seats

    # =========================================================
    # DOORS VALIDATION
    # =========================================================

    def clean_doors(self):
        doors = self.cleaned_data.get("doors")

        if doors is None:
            raise forms.ValidationError(
                "Number of doors is required."
            )

        if doors < 1:
            raise forms.ValidationError(
                "Doors must be at least 1."
            )

        return doors

    # =========================================================
    # MAINTENANCE COUNT VALIDATION
    # =========================================================

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

    # =========================================================
    # PLATE NUMBER VALIDATION
    # =========================================================

    def clean_plate_number(self):
        plate_number = (
            self.cleaned_data.get("plate_number")
        )

        if plate_number:
            plate_number = plate_number.strip().upper()

        return plate_number

    # =========================================================
    # FEATURES CLEANING
    # =========================================================

    def clean_features(self):
        features = self.cleaned_data.get("features")

        if not features:
            return ""

        # Clean unnecessary spaces around commas.
        cleaned_features = [
            feature.strip()
            for feature in features.split(",")
            if feature.strip()
        ]

        return ", ".join(cleaned_features)

    # =========================================================
    # CROSS-FIELD VALIDATION
    # =========================================================

    def clean(self):
        cleaned_data = super().clean()

        total_quantity = cleaned_data.get(
            "total_quantity"
        )

        maintenance_count = cleaned_data.get(
            "maintenance_count"
        )

        fleet_status = cleaned_data.get(
            "fleet_status"
        )

        maintenance_reason = cleaned_data.get(
            "maintenance_reason"
        )

        # -----------------------------------------------------
        # MAINTENANCE COUNT CANNOT EXCEED TOTAL FLEET
        # -----------------------------------------------------

        if (
            total_quantity is not None
            and maintenance_count is not None
            and maintenance_count > total_quantity
        ):
            self.add_error(
                "maintenance_count",
                (
                    "Maintenance count cannot be greater "
                    "than total quantity."
                ),
            )

        # -----------------------------------------------------
        # MAINTENANCE STATUS REQUIRES REASON
        # -----------------------------------------------------

        if (
            fleet_status == "Maintenance"
            and not maintenance_reason
        ):
            self.add_error(
                "maintenance_reason",
                (
                    "Maintenance reason is required when "
                    "the vehicle is under maintenance."
                ),
            )

        # -----------------------------------------------------
        # NON-MAINTENANCE STATUS
        # -----------------------------------------------------
        #
        # We intentionally DO NOT delete maintenance information
        # when the status changes. This allows staff to preserve
        # maintenance history/details instead of silently losing it.
        # -----------------------------------------------------

        return cleaned_data

class RentalInspectionForm(forms.ModelForm):
    class Meta:
        model = RentalInspection
        fields = ["mileage", "fuel_level", "notes", "damage_found", "damage_description"]
        widgets = {
            "mileage": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "fuel_level": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "damage_found": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "damage_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("damage_found") and not (cleaned.get("damage_description") or "").strip():
            self.add_error("damage_description", "Describe the damage found.")
        return cleaned


class ExtraChargeForm(forms.ModelForm):
    class Meta:
        model = ExtraCharge
        fields = ["charge_type", "description", "amount"]
        widgets = {
            "charge_type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Reason for charge"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": "0.01", "step": "0.01"}),
        }
