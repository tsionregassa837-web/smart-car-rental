from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views
from .views_reports import reports_dashboard


urlpatterns = [

    # =========================================================
    # PUBLIC PAGES
    # =========================================================

    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "about/",
        views.about,
        name="about",
    ),

    path(
        "cars/",
        views.cars,
        name="cars",
    ),

    path(
        "cars/<int:id>/",
        views.car_details,
        name="car_details",
    ),

    path(
        "contact/",
        views.contact,
        name="contact",
    ),


    # =========================================================
    # AUTHENTICATION
    # =========================================================

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "login/",
        views.user_login,
        name="login",
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout",
    ),


    # =========================================================
    # PASSWORD CHANGE
    # =========================================================

    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="core/password_change.html",
            success_url=reverse_lazy(
                "password_change_done"
            ),
        ),
        name="password_change",
    ),

    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="core/password_change_done.html",
        ),
        name="password_change_done",
    ),


    # =========================================================
    # PASSWORD RESET
    # =========================================================

    path(
        "password-reset/",
        views.password_reset_request,
        name="password_reset",
    ),

    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),

    path(
        "password-reset-complete/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),


    # =========================================================
    # CUSTOMER BOOKING
    # =========================================================

    path(
        "booking/",
        views.booking,
        name="booking",
    ),

    path(
        "my_bookings/",
        views.my_bookings,
        name="my_bookings",
    ),

    # Shared booking detail view - CUSTOMER
    path(
        "my_bookings/<int:booking_id>/",
        views.booking_detail,
        name="customer_booking_detail",
    ),

    path(
        "booking/<int:booking_id>/cancel/",
        views.cancel_booking,
        name="cancel_booking",
    ),

    path(
        "booking/<int:booking_id>/document/<str:document_type>/",
        views.booking_document,
        name="booking_document",
    ),


    # =========================================================
    # CUSTOMER PAYMENT
    # =========================================================

    path(
        "payment/<int:id>/",
        views.payment,
        name="payment",
    ),

    path(
        "payment-receipt/<int:id>/",
        views.payment_receipt,
        name="payment_receipt",
    ),

    path(
        "payment-history/",
        views.payment_history,
        name="payment_history",
    ),


    # =========================================================
    # CUSTOMER AREA
    # =========================================================

    path(
        "dashboard/",
        views.customer_dashboard,
        name="customer_dashboard",
    ),

    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    path(
        "notifications/",
        views.notifications,
        name="notifications",
    ),

    path(
        "account-settings/",
        views.account_settings,
        name="account_settings",
    ),


    # =========================================================
    # ADMIN / STAFF DASHBOARD
    # =========================================================

    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),

    path(
        "admin-profile/",
        views.admin_profile,
        name="admin_profile",
    ),

    path(
        "admin-settings/",
        views.admin_profile,
        name="admin_settings",
    ),

    path(
        "customer-management/",
        views.customer_management,
        name="customer_management",
    ),
    path(
        "customer-management/<int:user_id>/",
        views.customer_detail,
        name="customer_detail",
    ),


    # =========================================================
    # FLEET MANAGEMENT
    # =========================================================

    path(
        "fleet-management/",
        views.fleet_management,
        name="fleet_management",
    ),

    path(
        "fleet-management/add/",
        views.fleet_vehicle_add,
        name="fleet_vehicle_add",
    ),

    path(
        "fleet-management/<int:car_id>/",
        views.fleet_vehicle_detail,
        name="fleet_vehicle_detail",
    ),

    path(
        "fleet-management/<int:car_id>/edit/",
        views.fleet_vehicle_edit,
        name="fleet_vehicle_edit",
    ),

    path(
        "fleet-management/<int:car_id>/delete/",
        views.fleet_vehicle_archive,
        name="fleet_vehicle_archive",
    ),


    # =========================================================
    # BOOKING MANAGEMENT
    # =========================================================

    path(
        "booking-management/",
        views.booking_management,
        name="booking_management",
    ),

    # Shared booking detail view - STAFF
    path(
        "booking-management/<int:booking_id>/",
        views.booking_detail,
        name="staff_booking_detail",
    ),

    path(
        "booking-status/<int:booking_id>/<str:status>/",
        views.update_booking_status,
        name="update_booking_status",
    ),

    path(
        "verify-documents/<int:booking_id>/<str:action>/",
        views.verify_documents,
        name="verify_documents",
    ),

    path(
        "rental-action/<int:booking_id>/<str:action>/",
        views.rental_action,
        name="rental_action",
    ),


    # =========================================================
    # PAYMENT MANAGEMENT
    # =========================================================

    path(
        "payment-management/",
        views.payment_management,
        name="payment_management",
    ),

    path(
        "booking/<int:booking_id>/payment/mark-paid/",
        views.mark_payment_paid,
        name="mark_payment_paid",
    ),


    # =========================================================
    # REPORTS
    # =========================================================

    path(
        "reports/",
        reports_dashboard,
        name="reports_dashboard",
    ),
]