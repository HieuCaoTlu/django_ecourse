from django.contrib import admin
from .models import InvoiceRequest

class InvoiceRequestAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'amount', 'teacher_bank', 'teacher_bank_number', 'date']
    # Đảm bảo các trường đều là read-only, nếu cần
    readonly_fields = ['teacher', 'amount', 'teacher_bank', 'teacher_bank_number', 'date']

    def teacher_bank(self, obj):
        return obj.teacher.bank

    def teacher_bank_number(self, obj):
        return obj.teacher.bank_number

    # Thiết lập các tên cột cho các trường liên quan
    teacher_bank.short_description = 'Teacher Bank'
    teacher_bank_number.short_description = 'Teacher Bank Number'

# Đăng ký lớp admin với mô hình InvoiceRequest
admin.site.register(InvoiceRequest, InvoiceRequestAdmin)
