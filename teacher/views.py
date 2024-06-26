from django.shortcuts import redirect, render
from django.views import View
from base.models import *
from .models import InvoiceRequest
from django.db.models import Count, Avg, Case, When
from onlinecourse import settings
from .forms import CourseForm, SectionFormSet, SectionForm, LessonFormSet, DescriptionFormSet
from django.views.generic.edit import CreateView, UpdateView
from django.contrib import messages
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
class HomepageTeacher(View):

    def get(self, request):
        teacher = None
        all_courses = None
        if request.user.is_authenticated:
            teacher = Teacher.objects.filter(pk=request.user.id).first()
            if teacher:
                teacher.name = request.user.last_name
                all_courses = Course.objects.filter(teacher=teacher).annotate(
                    enroll=Count('enrollment', distinct=True),
                    vote=Avg(
                        Case(
                            When(enrollment__vote__gt=0, then='enrollment__vote'),
                            output_field=models.FloatField(),
                        )
                    ),
                )
                content = {
                'all_courses': all_courses,
                'logged': request.user.is_authenticated,
                'teacher' : teacher,
                'update_length': all_courses.count(),
                'valid_length': Course.objects.filter(teacher=teacher, validate=True, active=False).count(),
                'active_length': Course.objects.filter(teacher=teacher, active=True).count()
                }
                return render(request, template_name='teacher/homepage.html', context=content)
            else:
                messages.error(request, 'Vui lòng đăng nhập tài khoản giảng viên')
                return redirect('base:login')
        else:
            messages.error(request, 'Vui lòng đăng nhập tài khoản giảng viên')
            return redirect('base:login')
        
    def post(self, request):
        if request.user.is_authenticated:
            teacher = Teacher.objects.filter(pk=request.user.id).first()
            if teacher:
                teacher.name = request.user.last_name
                course = Course.objects.get(pk=request.POST.get('course'))
                course.validate = True
                course.save()
                return redirect('teacher:homepage')
            else:
                return redirect('base:login')
        else:
            return redirect('base:login')

class CourseInline():
    form_class = CourseForm
    model = Course
    template_name = "teacher/course_create_or_update.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        
        teacher = Teacher.objects.get(pk=self.request.user.id)
        self.object = form.save(commit=False)
        self.object.teacher = teacher
        self.object.save()

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        
        course_id = self.object.id
        return redirect('teacher:update_course',course_id)

    def formset_sections_valid(self, formset):
        sections = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for section in sections:
            section.course = self.object
            section.save()

    def formset_descriptions_valid(self, formset):
        descriptions = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for description in descriptions:
            description.course = self.object
            description.save()

class CourseCreate(CourseInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(CourseCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'sections': SectionFormSet(prefix='sections'),
                'descriptions': DescriptionFormSet(prefix='descriptions')
            }
        else:
            return {
                'sections': SectionFormSet(self.request.POST or None, prefix='sections'),
                'descriptions': DescriptionFormSet(self.request.POST or None, prefix='descriptions')
            }

class CourseUpdate(CourseInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(CourseUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'sections': SectionFormSet(self.request.POST or None, instance=self.object, prefix='sections'),
            'descriptions': DescriptionFormSet(self.request.POST or None, instance=self.object, prefix='descriptions')
        }

class SectionInline():
    form_class = SectionForm
    model = Section
    template_name = "teacher/section_create_or_update.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        
        teacher = Teacher.objects.get(pk=self.request.user.id)
        self.object = form.save(commit=False)
        self.object.teacher = teacher
        self.object.save()

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        section_id = self.object.id
        return redirect('teacher:update_section',section_id)

    def formset_lessons_valid(self, formset):
        lessons = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for lesson in lessons:
            lesson.section = self.object
            if not lesson.document:
                file = lesson.file
                print(file.name)
                storage = settings.firebase.storage()
                storage_path = "documents/" + file.name
                print(storage_path, file)
                storage.child(storage_path).put(file)
                lesson.document = storage.child(storage_path).get_url(None)
            lesson.save()

class SectionUpdate(SectionInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(SectionUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        ctx['course_id'] = self.object.course.id
        return ctx

    def get_named_formsets(self):
        return {
            'lessons': LessonFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='lessons'),
        }

class IncomeTeacher(View):
    def get(self, request):
        teacher = None
        if request.user.is_authenticated:
            teacher = Teacher.objects.filter(pk=request.user.id).first()
            if teacher:
                enrolled = Enrollment.objects.filter(course__teacher=teacher)
                courses = Course.objects.filter(teacher=teacher)
                course_enrollments = []
                for course in courses:
                    enrollments = Enrollment.objects.filter(course=course)
                    total_enrollments = enrollments.count()
                    course_enrollments.append({
                        'course': course,
                        'total_enrollments': total_enrollments,
                        'percentage': total_enrollments / len(enrolled) * 100 if len(enrolled) > 0 else 0
                    })
                enrolled_by_date = {}
                for enrollment in enrolled:
                    date_key = enrollment.enroll_date.strftime('%Y-%m-%d')
                    enrolled_by_date[date_key] = enrolled_by_date.get(date_key, 0) + 1
                invoices = InvoiceRequest.objects.filter(teacher=teacher)
                invoices_data = [
                    {'amount': invoice.amount, 
                     'date': invoice.date.strftime("%Y-%m-%d %H:%M:%S"), 
                     'status': 'Đã thanh toán' if invoice.status else 'Đang xử lý'
                    } for invoice in invoices]
                invoices_json = json.dumps(invoices_data, cls=DjangoJSONEncoder)
                valid = request.session.pop('valid', None)
                print(invoices)
                content = {
                'enrolled': enrolled,
                'logged': request.user.is_authenticated,
                'teacher' : teacher,
                'enrolled_by_date': enrolled_by_date,
                'course_enrollments': course_enrollments,
                'invoices_json': invoices_json,
                'valid': valid
                }

                return render(request, template_name='teacher/income.html', context=content)
            else:
                messages.error(request, 'Vui lòng đăng nhập tài khoản giảng viên')
                return redirect('base:login')
        else:
            messages.error(request, 'Vui lòng đăng nhập tài khoản giảng viên')
            return redirect('base:login')
        
    def post(self, request):
        if request.user.is_authenticated and request.user.teacher:
            teacher = Teacher.objects.filter(pk=request.user.id).first()
            if teacher.earning:
                invoice = InvoiceRequest()
                invoice.teacher = teacher
                invoice.amount = teacher.earning
                invoice.save()
                teacher.earning = 0
                teacher.save()
                request.session['valid'] = True
                return redirect('teacher:income')   
            else:
                messages.error(request, 'Ví của bạn trống!')
                return redirect('teacher:income')
        else:
            return HttpResponse("<script>alert('Giao dịch không hợp lệ!');history.back();</script>")