from django.contrib.auth.forms import UserCreationForm as CreForm, UserChangeForm as ChangeForm
from django.contrib.auth.models import Group
from .models import *
from django import forms
from onlinecourse import settings
from PIL import Image
from io import BytesIO
import os

class UserCreationForm(CreForm):

    def save(self, commit=True):
        user = self.instance
        user.is_staff = True 
        return super().save(commit=True)

    class Meta:
        model = User
        fields = ('first_name','last_name','phone','gender','birth_date')

class UserChangeForm(ChangeForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','phone','gender','birth_date')

class TeacherCreationForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)  
        user.is_staff = True  
        teacher_group = Group.objects.get_or_create(name='Teacher')[0]
        teacher_group.user_set.add(user)
        user.save()
        return user

    class Meta:
        model = Teacher
        fields = UserCreationForm.Meta.fields + ('level','username','email','bank','bank_number')

class TeacherChangeForm(UserChangeForm):
    class Meta:
        model = Teacher
        fields = UserChangeForm.Meta.fields + ('level','email','bank','bank_number')

class StudentCreationForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return user

    class Meta:
        model = Student
        fields = UserCreationForm.Meta.fields + ('major','username','email')

class StudentChangeForm(UserChangeForm):
    class Meta:
        model = Student
        fields = UserChangeForm.Meta.fields + ('major','email')

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def save(self, commit=True):
        course = super().save(commit=False)
        if 'image' in self.files:
            image = self.files['image']

            img = Image.open(image)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=60) 
            img_io.seek(0)

            self.files['image'] = img_io

            storage = settings.firebase.storage()
            storage_path = "courses/" + image.name
            storage.child(storage_path).put(img_io)
            course.cover = storage.child(storage_path).get_url(None)
        if commit:
            course.active = False
            course.save()
        return course
    
class LessonAdminForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title','document_type','file']

    def save(self, commit=True):
        lesson = super().save(commit=False)
        if 'file' in self.files:
            file = self.files['file']
            storage = settings.firebase.storage()
            storage_path = "documents/" + file.name
            storage.child(storage_path).put(file)
            lesson.document = storage.child(storage_path).get_url(None)
        if commit:
            lesson.save()
        return lesson
    
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def save(self, commit=True):
        category = super().save(commit=False)
        if 'image' in self.files:
            image = self.files['image']

            img = Image.open(image)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=60) 
            img_io.seek(0)

            self.files['image'] = img_io

            storage = settings.firebase.storage()
            storage_path = "category/" + image.name
            storage.child(storage_path).put(img_io)
            category.cover = storage.child(storage_path).get_url(None)
        if commit:
            category.save()
            os.remove(image.path)
        return category
    
class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'

class CourseDescForm(forms.ModelForm):
    class Meta:
        model = CourseDescription
        fields = '__all__'    
    