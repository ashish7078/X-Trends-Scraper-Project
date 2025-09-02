from django.db import models
import uuid

class TrendRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trend1 = models.CharField(max_length=255)
    trend2 = models.CharField(max_length=255)
    trend3 = models.CharField(max_length=255)
    trend4 = models.CharField(max_length=255)
    trend5 = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    run_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This will show the object with its date in the Django admin
        return f"Trend Run at {self.run_timestamp.strftime('%Y-%m-%d %H:%M')}"