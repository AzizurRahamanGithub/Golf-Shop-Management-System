from django import forms
from django.utils.safestring import mark_safe
from .models import Blog
from apps.file_uploader.upload_utils import upload_file_to_digital_ocean, delete_file_from_digital_ocean


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


class BlogAdminForm(forms.ModelForm):
    upload_image = forms.FileField(required=False, help_text="Upload single image")
    delete_image = forms.BooleanField(
        required=False, initial=False, help_text="Check to delete current single image"
    )
    upload_images = MultiFileField(required=False, help_text="Upload multiple images")
    delete_images = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        help_text="Check images to delete"
    )

    class Meta:
        model = Blog
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- single image preview with checkbox ---
        if getattr(self.instance, "image", None):
            img_url = self.instance.image
            self.fields["delete_image"].help_text = mark_safe(
                f'<img src="{img_url}" style="max-height:100px; margin:5px; border:1px solid #ccc; border-radius:6px;"><br>'
                "Check to delete this image"
            )

        # --- multiple images preview with checkboxes ---
        if getattr(self.instance, "images", None):
            choices = [(url, mark_safe(f'<img src="{url}" style="max-height:80px; margin:5px; border:1px solid #ccc; border-radius:6px;">'))
                       for url in self.instance.images]
            self.fields["delete_images"].choices = choices

            html = "".join([f'<img src="{url}" style="max-height:80px; margin:5px; border:1px solid #ccc; border-radius:6px;">'
                            for url in self.instance.images])
            self.fields["upload_images"].help_text = mark_safe(f"Existing multiple images:<br>{html}")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # --- SINGLE IMAGE DELETE ---
        if self.cleaned_data.get("delete_image") and getattr(instance, "image", None):
            try:
                delete_file_from_digital_ocean(instance.image)
            except Exception:
                pass
            instance.image = None

        # --- SINGLE IMAGE UPLOAD ---
        single_file = self.cleaned_data.get("upload_image")
        if single_file:
            if getattr(instance, "image", None):
                try:
                    delete_file_from_digital_ocean(instance.image)
                except Exception:
                    pass
            instance.image = upload_file_to_digital_ocean(single_file, folder="blogs")

        # --- MULTIPLE IMAGES DELETE ---
        to_delete = self.cleaned_data.get("delete_images") or []
        if to_delete:
            for url in to_delete:
                try:
                    delete_file_from_digital_ocean(url)
                except Exception:
                    pass
            instance.images = [url for url in getattr(instance, "images", []) if url not in to_delete]

        # --- MULTIPLE IMAGES UPLOAD ---
        new_files = self.cleaned_data.get("upload_images") or []
        all_urls = list(getattr(instance, "images", []) or [])
        for f in new_files:
            if f:
                url = upload_file_to_digital_ocean(f, folder="blogs")
                all_urls.append(url)

        # unique list
        instance.images = list(dict.fromkeys(all_urls))

        if commit:
            instance.save()
        return instance
