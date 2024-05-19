
import random
import string
from django.core.mail import EmailMessage
from django.conf import settings
 
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_email(email, otp):
    try:
        email = EmailMessage(
            'Beyond: Xác thực OTP cho tài khoản mới',
            f"Mã OTP của bạn là: {otp}. Mã sẽ hết hạn sau 5 phút.",
            settings.EMAIL_HOST_USER,
            [email],
        )
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gửi email: {e}")
        return False