import logging

from django.db import connection
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocumentUploadForm
from .models import Document

logger = logging.getLogger(__name__)


def healthz(request):
    """Liveness probe: the process is up and serving requests."""
    return JsonResponse({"status": "ok"})


def readyz(request):
    """Readiness probe: the app can reach its database."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "unavailable", "database": "down"}, status=503)
    return JsonResponse({"status": "ok", "database": "up"})


def document_list(request):
    """Upload form plus the list of documents."""
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            uploaded = form.cleaned_data["file"]
            document.original_name = uploaded.name
            document.content_type = getattr(uploaded, "content_type", "") or ""
            document.size_bytes = uploaded.size
            document.save()
            logger.info("Document uploaded: id=%s size=%s", document.pk, document.size_bytes)
            return redirect("document_list")
    else:
        form = DocumentUploadForm()

    return render(
        request,
        "document_list.html",
        {"form": form, "documents": Document.objects.all()[:50]},
    )


def share_download(request, token):
    """Serve a file by its share token, if the link has not expired."""
    document = get_object_or_404(Document, share_token=token)

    if document.is_expired:
        logger.info("Expired share link requested: id=%s", document.pk)
        raise Http404("This share link has expired.")

    Document.objects.filter(pk=document.pk).update(
        download_count=document.download_count + 1
    )
    logger.info("Document downloaded: id=%s", document.pk)

    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.original_name,
    )
