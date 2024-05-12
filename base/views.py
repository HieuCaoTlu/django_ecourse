from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout 
from django.shortcuts import render, redirect
from base.forms import StudentCreationForm, StudentChangeForm, TeacherCreationForm, TeacherChangeForm
from django.views import View
from base.models import Student, Teacher

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
            form.save()
            request.session['login_valid'] = 'REGISTER_SUCCESS'
            return redirect('base:login')
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
