from django.core.files.storage import Storage
from vercel.blob import delete, head, put, get
from django.conf import settings

from django.urls import reverse

class VercelBlobStorage(Storage):

    def _save(self, name, content):
        blob = put(
            name,
            content,
            access="private",
            content_type=getattr(content, "content_type", None),
            add_random_suffix=False,
        )

        return blob.pathname

    def exists(self, name):
        try:
            head(name)
            return True
        except Exception:
            return False

    def delete(self, name):
        delete(name)

    def url(self, name):
        return reverse("serve_private_blob", kwargs={"pathname": name})
