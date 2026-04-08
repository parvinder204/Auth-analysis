from django.db import models


class LoginLog(models.Model):
    username = models.CharField(max_length=150)
    method = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField(default=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.username} - {self.method} - {self.timestamp}"