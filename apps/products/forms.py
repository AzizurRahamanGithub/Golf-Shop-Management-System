from django import forms
from apps.file_uploader.upload_utils import upload_file_to_digital_ocean, delete_file_from_digital_ocean
from django.utils.safestring import mark_safe


# -----------------------------
# Single Image Form
# -----------------------------
class SingleImageForm(forms.ModelForm):
    upload_image = forms.FileField(required=False, help_text="Upload single image")
    delete_image = forms.BooleanField(
        required=False, initial=False, help_text="Check to delete this image"
    )
    image_folder = "uploads"  # default folder, override in child form

    class Meta:
        model = None  # set in child
        fields = "__all__"

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Delete existing image if checkbox checked
        if self.cleaned_data.get("delete_image") and getattr(instance, "image", None):
            try:
                delete_file_from_digital_ocean(instance.image)
            except Exception:
                pass
            instance.image = None

        # Upload new image
        file = self.cleaned_data.get("upload_image")
        if file:
            if getattr(instance, "image", None):
                try:
                    delete_file_from_digital_ocean(instance.image)
                except Exception:
                    pass
            instance.image = upload_file_to_digital_ocean(file, folder=self.image_folder)

        if commit:
            instance.save()
        return instance

# -----------------------------
# Multi file input
# -----------------------------
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultiFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)

# -----------------------------
# Multiple Images Form
# -----------------------------
class MultipleImagesForm(forms.ModelForm):
    upload_images = MultiFileField(
        required=False, help_text="Upload multiple images"
    )
    delete_images = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        help_text="Select images to delete"
    )
    image_folder = "uploads"

    class Meta:
        model = None  # set in child
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        images = getattr(self.instance, "images", []) or []

        # --- populate delete_choices with preview ---
        choices = []
        for url in images:
            html = mark_safe(f'<img src="{url}" style="max-height:80px; margin:5px; border:1px solid #ccc; border-radius:6px;">')
            choices.append((url, html))
        self.fields["delete_images"].choices = choices

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Delete selected images
        to_delete = self.cleaned_data.get("delete_images") or []
        if to_delete:
            for url in to_delete:
                try:
                    delete_file_from_digital_ocean(url)
                except Exception:
                    pass
            instance.images = [url for url in getattr(instance, "images", []) if url not in to_delete]

        # Upload new images
        new_files = self.cleaned_data.get("upload_images") or []
        all_urls = list(getattr(instance, "images", []) or [])
        for f in new_files:
            if f:
                url = upload_file_to_digital_ocean(f, folder=self.image_folder)
                all_urls.append(url)

        instance.images = list(dict.fromkeys(all_urls))  # unique urls

        if commit:
            instance.save()
        return instance