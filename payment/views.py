from django.shortcuts import render, redirect
from django.views import View
from .vnpay import *
from .forms import *
from django.http import HttpResponse
from base.models import Course, Student
from .models import *

# Create your views here.
class Payment(View):

    def get(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        try:
            student = Student.objects.get(pk=request.user.id)
        except Student.DoesNotExist:
            return redirect('base:login')
        return render(request, "payment/payment.html", {"title": "Thanh toán", "course":course, "student":student})
    
    def post(self, request, course_id):
        form = PaymentForm(request.POST)
        result = active_payment(request,form,course_id)
        if result:
            return redirect(result)
        return HttpResponse('Failed')
    
class PaymentReturn(View):
    
    def get(self, request, course_id):
        result = payment_return(request)
        response = request.GET
        content = {
            'order_id':response['vnp_TxnRef'],
            'amount':int(response['vnp_Amount']) / 100,
            'order_desc':response['vnp_OrderInfo'],
            'vnp_TransactionNo':response['vnp_TransactionNo'],
            'vnp_ResponseCode':response['vnp_ResponseCode'],
            'course_id': course_id
        }
        if result:
            info = PaymentInfo()
            info.amount = int(response['vnp_Amount']) / 100
            info.code = response['vnp_ResponseCode']
            info.bank = response['vnp_BankCode']
            info.date = datetime.strptime(response['vnp_PayDate'], '%Y%m%d%H%M%S')
            info.save()
            request.session['info_id'] = info.id
            return render(request,template_name="payment/success.html",context=content)
        return HttpResponse('Failed')
    

# Ngân hàng	NCB
# Số thẻ	9704198526191432198
# Tên chủ thẻ	NGUYEN VAN A
# Ngày phát hành	07/15
# Mật khẩu OTP	123456