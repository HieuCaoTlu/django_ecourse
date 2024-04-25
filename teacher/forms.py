from io import BytesIO
from django.forms import ModelForm, TextInput, inlineformset_factory, Select, FileInput
from base.models import Course, Section, Lesson
from onlinecourse import settings
from PIL import Image
from base.forms import LessonAdminForm

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['title','image','category']

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
    
class SectionFormInline(ModelForm):

    class Meta:
        model = Section
        fields = '__all__'
        widgets = {
            'title': TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
        }

class SectionForm(ModelForm):

    class Meta:
        model = Section
        fields = '__all__'

class LessonFormInline(ModelForm):

    class Meta:
        model = Lesson
        fields = ['title','document_type','file']

SectionFormSet = inlineformset_factory(
    Course, Section, form=SectionFormInline,
    extra=1, can_delete=True, can_delete_extra=True
)

LessonFormSet = inlineformset_factory(
    Section, Lesson, form=LessonAdminForm,
    extra=1, can_delete=True, can_delete_extra=True
)