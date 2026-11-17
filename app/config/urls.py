from django.contrib import admin
from django.urls import path

from documents import views

urlpatterns = [
    path("", views.document_list, name="document_list"),
    path("s/<uuid:token>/", views.share_download, name="share_download"),
    path("healthz", views.healthz, name="healthz"),
    path("readyz", views.readyz, name="readyz"),
    path("admin/", admin.site.urls),
]
