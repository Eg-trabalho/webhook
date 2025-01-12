from django.db import models

class garota(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=100, null=True, blank=True)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.nickname}"
