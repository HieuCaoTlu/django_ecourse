from django.db import models
from base.models import Teacher
from django.utils import timezone

# Create your models here.
class InvoiceRequest(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING)
    amount = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.teacher}: {self.amount}"
    
    class Meta:
        verbose_name = 'Hóa đơn giảng viên'
        verbose_name_plural = 'Hóa đơn giảng viên'