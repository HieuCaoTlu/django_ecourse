from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout 
from django.shortcuts import render, redirect
from base.forms import OTPVerificationForm, StudentCreationForm, StudentChangeForm, TeacherCreationForm, TeacherChangeForm
from django.views import View
from base.models import Student, Teacher, User
from base.tests import send_email, generate_otp
# Create your views here.
class Login(View):

    def get(self, request):
        valid = request.session.pop('login_valid',None)
        return render(request,'base/login.html',{'valid':valid})
    
    def post(self, request):
        username = request.POST.get('username')
        psw = request.POST.get('psw')
        user = authenticate(username=username, password=psw)
        if not user:
            return render(request,'base/login.html',{'message':'FAIL',})
        login(request, user)
        if hasattr(user, 'teacher'):
            return redirect('teacher:homepage')
        else:
            return redirect('course:homepage')
    
class Logout(View):

    def get(self, request):
        logout(request)
        return redirect('base:login')
    
class ChooseRole(View):

    def get(self, request):
        return render(request,template_name='base/role.html')
    
class Register(View):
    def get(self, request, role_type):
        if role_type == 'student':
            form = StudentCreationForm() 
        else:
            form = TeacherCreationForm()
        return render(request, 'base/register.html', {'form': form, 'message':'REGISTER'})  
    
    def post(self, request, role_type):
        if role_type == 'student':
            form = StudentCreationForm(request.POST)
        else:
            form = TeacherCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            otp = generate_otp()
            request.session['otp'] = otp
            send_email(user.email, otp)
            request.session['user_id'] = user.id
            return redirect('base:verify_otp')
        if role_type == 'student':
            form = StudentCreationForm()
        else:
            form = TeacherCreationForm()
        return render(request, 'base/register.html', {'form': form, 'message':'FAIL'})
    
class Personal(View):
    def get(self, request):
        if hasattr(request.user, 'student'):
            student = Student.objects.get(pk=request.user.id)
            form = StudentChangeForm(instance=student)
        else:
            teacher = Teacher.objects.get(pk=request.user.id)
            form = TeacherChangeForm(instance=teacher)
        return render(request, 'base/personal.html', {'form': form, 'message':'REGISTER'})  
    
    def post(self, request):
        if hasattr(request.user, 'student'):
            student = Student.objects.get(pk=request.user.id)
            form = StudentChangeForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                return redirect('base:personal')
            else:
                form = StudentChangeForm(instance=student)
        else:
            teacher = Teacher.objects.get(pk=request.user.id)
            form = TeacherChangeForm(request.POST,instance=teacher)     
            if form.is_valid():
                form.save()
                return redirect('base:personal')
            else:
                form = TeacherChangeForm(instance=teacher)       
        return render(request, 'base/personal.html', {'form': form, 'message':'FAIL'})

class VerifyOTP(View):
    def get(self, request):
        if request.session.get('otp',None):
            form = OTPVerificationForm()
            return render(request, 'base/verify_otp.html', {'form': form})
        else:
            return redirect('base:login')

    def post(self, request):
        form = OTPVerificationForm(request.POST)
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('base:register')

        otp = request.session.get('otp')

        if form.is_valid() and otp:
            if form.cleaned_data['otp'] == otp:
                try:
                    user = User.objects.get(pk=user_id)
                    user.is_active = True
                    user.save()
                    del request.session['user_id']
                    del request.session['otp']
                    request.session['login_valid'] = 'REGISTER_SUCCESS'
                    return redirect('base:login')
                except User.DoesNotExist:
                    message = 'User not found'
            else:
                message = 'Nhập sai mã OTP hoặc mã đã hết hạn'
        else:
            message = 'Trường thông tin không chính xác'

        return render(request, 'base/verify_otp.html', {'form': form, 'message': message})