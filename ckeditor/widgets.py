from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode

from django.core.exceptions import ImproperlyConfigured
from django.forms.util import flatatt

class CKEditorWidget(forms.Textarea):
    """
    Widget providing CKEditor for Rich Text Editing.
    Supports direct image uploads and embed.
    """
    class Media:
        try:
            js = (
                settings.CKEDITOR_MEDIA_PREFIX + 'ckeditor/ckeditor.js',
            )
        except AttributeError:
            raise ImproperlyConfigured("django-ckeditor requires CKEDITOR_MEDIA_PREFIX setting.")
    
    def render(self, name, value, attrs={}):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        default_editor_options = {
            'skin': "v2",
            'toolbar': "Full",
            'height': "291", 
            'width': "618",
            'filebrowserUploadUrl': reverse('ckeditor_upload'),
            'filebrowserBrowseUrl': reverse('ckeditor_browse'),
            'filebrowserWindowWidth': '940',
            'filebrowserWindowHeight': '747',
        }
        default_editor_options.update(getattr(settings, "CKEDITOR_OPTIONS", {}))
        return mark_safe(u'''<textarea%s>%s</textarea>
        <script type="text/javascript">
            CKEDITOR.replace("%s",
                    %s
            );
        </script>''' % (flatatt(final_attrs), conditional_escape(force_unicode(value)), final_attrs['id'], str(default_editor_options)))
