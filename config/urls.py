"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # ============================================================
    # DJANGO ADMIN
    # ============================================================
    path(
        "admin/",
        admin.site.urls,
    ),

    # ============================================================
    # CORE APPLICATION
    # ============================================================
    path(
        "",
        include("core.urls"),
    ),
]


# ============================================================
# MEDIA FILES — DEVELOPMENT ONLY
# ============================================================
#
# Customer documents such as:
# - Driver's License
# - National ID
#
# must NOT be exposed through a public /media/ URL in production.
#
# The protected booking_document view in core/views.py handles
# secure document access.
#
# This development helper is intentionally enabled only when
# DEBUG=True.
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )