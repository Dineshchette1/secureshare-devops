from django import forms

from .models import Document

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".png", ".jpg", ".jpeg", ".zip",
}


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Quarterly report"}),
        }

    def clean_file(self):
        uploaded = self.cleaned_data["file"]

        if uploaded.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError(
                f"File is too large ({uploaded.size // 1024 // 1024} MB). The limit is 10 MB."
            )

        name = uploaded.name.lower()
        if not any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise forms.ValidationError("That file type is not allowed.")

        return uploaded
