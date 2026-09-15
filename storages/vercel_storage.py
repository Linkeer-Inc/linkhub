from django.core.files.storage import Storage
from vercel.blob import delete, head, put
from django.conf import settings

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
        return f"{settings.VERCEL_BLOB_BASE_URL}/{name}"
