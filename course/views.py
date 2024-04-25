from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.db.models import Count, Avg, Case, When
from base.forms import StudentChangeForm
from base.models import *
from django.http import HttpResponse
from django.db.models import OuterRef, Exists, Value
from payment.models import PaymentInfo
from .certificate import make_certificates

class HomepageCourse(View):

    def get(self, request):
        student = None
        if request.user.is_authenticated:
            student = Student.objects.filter(pk=request.user.id).first()
            if student:
                student.name = request.user.last_name

        all_courses = Course.objects.filter(active=True).annotate(
            enroll=Count('enrollment', distinct=True),
            vote=Avg(
                Case(
                    When(enrollment__vote__gt=0, then='enrollment__vote'),
                    output_field=models.FloatField(),
                )
            ),
            user_enroll=Exists(
                Enrollment.objects.filter(course=OuterRef('pk'), student=student)
            )
        )

        all_categories = Category.objects.all()

        content = {
            'all_courses': all_courses,
            'message': 'FOUND' if all_courses.exists() else 'NOT_FOUND',
            'logged': request.user.is_authenticated,
            'student' : student  ,
            'all_categories':all_categories
        }
        return render(request, template_name='course/homepage.html', context=content)
    
class CategoryCourse(View):

    def get(self, request,category_id):
        student = None
        category = Category.objects.get(pk=category_id)
        if request.user.is_authenticated:
            student = Student.objects.filter(pk=request.user.id).first()
            if student:
                student.name = request.user.last_name

        all_courses = Course.objects.filter(active=True,category=category).annotate(
            enroll=Count('enrollment', distinct=True),
            vote=Avg(
                Case(
                    When(enrollment__vote__gt=0, then='enrollment__vote'),
                    output_field=models.FloatField(),
                )
            ),
            user_enroll=Exists(
                Enrollment.objects.filter(course=OuterRef('pk'), student=student)
            )
        )

        content = {
            'all_courses': all_courses,
            'message': 'FOUND' if all_courses.exists() else 'NOT_FOUND',
            'logged': request.user.is_authenticated,
            'student' : student  ,
            'category':category
        }
        return render(request, template_name='course/category.html', context=content)

class DetailCourse(View):

    def get(self, request, course_id):
        course_query = Course.objects.filter(pk=course_id, active=True).annotate(
            enroll=Count('enrollment', distinct=True),
            vote=Avg(
                Case(
                    When(enrollment__vote__gt=0, then='enrollment__vote'),
                    output_field=models.FloatField(),
                )
            ),
            sect=Count('section', distinct=True)
        )
        course = get_object_or_404(course_query)
        enrollment = None
        
        if request.user.is_authenticated:
            try:
                student = Student.objects.get(pk=request.user.id)
                if Enrollment.objects.filter(course=course, student=student).exists():
                    enrollment = Enrollment.objects.get(course=course, student=student)
            except Student.DoesNotExist:
                pass

        sections_query = Section.objects.filter(course=course, active=True)
        sections = dict()
        completed_course = True
        for section in sections_query:
            temp = Lesson.objects.filter(section=section,active=True).annotate(
                completed=Value(False),
                unlock=Value(False),
                score=Value(0)
            )   
            if enrollment:
                temp = Lesson.objects.filter(section=section,active=True)
                for lesson in temp:
                    process = LessonProcess.objects.get(enrollment=enrollment, lesson=lesson)
                    lesson.unlock = True
                    lesson.completed = process.completed
                    lesson.score = process.score
                    if process.completed == False:
                        completed_course = False
            sections[section] = temp
            section.range = len(temp)
        
        if completed_course and enrollment and enrollment.certificate == '':
            enrollment.completed = True
            cert_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
            cert_course = course.title
            cert_date = ''
            enrollment.certificate = make_certificates(cert_name, cert_course, cert_date)
            enrollment.save()

        if len(sections) > 0:
            first_section = next(iter(sections.keys()))
            lessons_set = sections[first_section]
            for lesson in lessons_set:
                if not lesson.unlock:
                    lesson.unlock = True

        content = {
            'course': course,
            'sections' : sections,
            'enrollment': enrollment,
            'message': 'FOUND' if enrollment else 'NOT_FOUND',
        }
        return render(request, template_name='course/course.html', context=content)
    
    def post(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        if request.user.is_authenticated:
            try:
                student = Student.objects.get(pk=request.user.id)
                try:
                    enrollment = Enrollment.objects.get(course=course, student=student)
                    return HttpResponse("<script>alert('Bạn đã đăng kí khóa học này trước đó');history.back()</script>")
                except Enrollment.DoesNotExist:
                    enrollment = Enrollment.objects.create(course=course, student=student)
                    info = PaymentInfo.objects.get(pk=request.session.get('info_id', None))
                    info.enrollment = enrollment
                    info.save()
                    del request.session['course_id']
                    del request.session['info_id']
                    lessons = Lesson.objects.filter(section__course=course)
                    for each in lessons:
                        lesson = Lesson.objects.get(pk=each.id)
                        LessonProcess.objects.create(lesson=lesson, enrollment=enrollment)
                return redirect('course:detail_course', course_id=course_id)
            except Student.DoesNotExist:
                return HttpResponse("<script>alert('Bạn chưa đăng kí tài khoản học sinh');history.back()</script>")
        else:
            return redirect('course:login')
   
class DetailLesson(View):
    def get(self, request, course_id, section_id, lesson_id):
        try:
            course = Course.objects.get(pk=course_id)
            section = Section.objects.get(pk=section_id)
            lesson = Lesson.objects.get(pk=lesson_id)
            enrollment = None
            message = None
            if request.user.is_authenticated:
                try:
                    student = Student.objects.get(pk=request.user.id)
                    if Enrollment.objects.filter(course=course, student=student).exists():
                        enrollment = Enrollment.objects.get(course=course, student=student)
                        process = LessonProcess.objects.get(enrollment=enrollment, lesson=lesson)
                        lesson.completed = process.completed
                        lesson.score = process.score
                        lesson.bookmark = process.bookmark
                        message = 'LOGGED'
                except Student.DoesNotExist:
                    lesson.completed = None
                    lesson.score = 0
                    lesson.bookmark = None
                    pass
            lesson.course_temp = course
            lesson.section_temp = section
            content = {
                'lesson': lesson,
                'message': message,
            }
        except Course.DoesNotExist:
            return HttpResponse("<script>alert('Không tìm thấy khóa học');history.back()</script>")
        except Section.DoesNotExist:
            return HttpResponse("<script>alert('Không tìm thấy phần học');history.back()</script>")
        except Lesson.DoesNotExist:
            return HttpResponse("<script>alert('Không tìm thấy bài học');history.back()</script>")
        return render(request, template_name='course/lesson.html',context=content)
    
    def post(self, request, course_id, section_id, lesson_id):
        try:
            course = Course.objects.get(pk=course_id)
            lesson = Lesson.objects.get(pk=lesson_id)
            student = Student.objects.get(pk=request.user.id)
            enrollment = Enrollment.objects.get(course=course, student=student)
            process = LessonProcess.objects.get(enrollment=enrollment, lesson=lesson)
            if 'complete_lesson' in request.POST:
                process.completed = True
                process.score = 10
            if 'add_bookmark' in request.POST:
                process.bookmark = True
            elif 'remove_bookmark' in request.POST:
                process.bookmark = False
            process.save()
        except Course.DoesNotExist:
            return HttpResponse("<script>alert('Không tìm thấy khóa học');history.back()</script>")
        except Section.DoesNotExist:
            return HttpResponse("<script>alert('Không tìm thấy phần học');history.back()</script>")
        except Lesson.DoesNotExist:
            return HttpResponse("<script>alert('Không tìm thấy bài học');history.back()</script>")
        return HttpResponse("<script>history.back()</script>")

class OverviewCourse(View):
    def get(self, request, course_id):
        course_query = Course.objects.filter(pk=course_id, active=True).annotate(
            enroll=Count('enrollment', distinct=True),
            vote=Avg(
                Case(
                    When(enrollment__vote__gt=0, then='enrollment__vote'),
                    output_field=models.FloatField(),
                )
            ),
            sect=Count('section', distinct=True)
        )
        course = get_object_or_404(course_query)
        reviewer = Enrollment.objects.filter(course_id=course_id, vote__gt=0).order_by('-vote')[:9]
        enrollment = None
        overview = CourseDescription.objects.get(course=course)
        if request.user.is_authenticated:
                try:
                    student = Student.objects.get(pk=request.user.id)
                    if Enrollment.objects.filter(course=course, student=student).exists():
                        enrollment = Enrollment.objects.get(course=course, student=student)
                except Student.DoesNotExist:
                    pass

        vote_count = {1:0,2:0,3:0,4:0,5:0}
        for person in reviewer:
            vote_count[int(person.vote)] += 1
        
        vote_dct = {}
        if reviewer:
            for vote, item in vote_count.items():
                vote_dct[vote] = int(item/sum(vote_count.values()) * 100)

            top_reviewers_dict = {'first': [], 'second': [], 'third': []}
            for i, reviewer in enumerate(reviewer):
                reviewer.vote = int(reviewer.vote)
                if i < 3:
                    top_reviewers_dict['first'].append(reviewer)
                elif 3 <= i < 6:
                    top_reviewers_dict['second'].append(reviewer)
                else:
                    top_reviewers_dict['third'].append(reviewer)

            course.vote_dct = vote_dct
            course.review = top_reviewers_dict
        content = {
            'course': course,
            'enrollment': enrollment,
            'overview':overview,
            'message': 'FOUND' if enrollment else 'NOT_FOUND',
        }
        return render(request,template_name='course/overview.html',context=content)

    def post(self, request, course_id):
        course = Course.objects.get(pk=course_id)
        student = Student.objects.get(pk=request.user.id)
        enrollment = Enrollment.objects.get(course=course, student=student)
        enrollment.vote = request.POST.get('vote')
        enrollment.review = request.POST.get('comment')
        enrollment.save()
        return redirect('course:overview_course',course_id)

class BookmarkCourse(View):
    def get(self, request, course_id):
        course_query = Course.objects.filter(pk=course_id, active=True).annotate(
            enroll=Count('enrollment', distinct=True),
            vote=Avg(
                Case(
                    When(enrollment__vote__gt=0, then='enrollment__vote'),
                    output_field=models.FloatField(),
                )
            ),
            sect=Count('section', distinct=True)
        )   
        course = get_object_or_404(course_query)
        student = Student.objects.get(pk=request.user.id)
        enrollment = Enrollment.objects.get(course=course, student=student)
        process_with_bookmark = LessonProcess.objects.filter(enrollment=enrollment, bookmark=True)
        sections = {}
        sections_query = Section.objects.filter(course=course, active=True)
        for section in sections_query:
            lessons_in_section = Lesson.objects.filter(section=section, active=True)            
            bookmarked_lessons = lessons_in_section.filter(
                id__in=process_with_bookmark.values_list('lesson_id', flat=True)
            )

            for lesson in bookmarked_lessons:
                try:
                    process = LessonProcess.objects.get(enrollment=enrollment, lesson=lesson)
                    lesson.completed = process.completed
                    lesson.score = process.score
                except LessonProcess.DoesNotExist:
                    pass

            if bookmarked_lessons.exists():
                sections[section] = bookmarked_lessons
        content = {
            'course': course,
            'enrollment': enrollment,
            'sections': sections,
            'message': 'FOUND' if enrollment else 'NOT_FOUND',
        }
        return render(request,template_name='course/bookmark.html',context=content)
    
class CertificateCourse(View):
    def get(self, request, course_id):
        course_query = Course.objects.filter(pk=course_id, active=True).annotate(
            enroll=Count('enrollment', distinct=True),
            vote=Avg(
                Case(
                    When(enrollment__vote__gt=0, then='enrollment__vote'),
                    output_field=models.FloatField(),
                )
            ),
            sect=Count('section', distinct=True)
        )
        course = get_object_or_404(course_query)
        enrollment = None
        overview = CourseDescription.objects.get(course=course)
        if request.user.is_authenticated:
                try:
                    student = Student.objects.get(pk=request.user.id)
                    if Enrollment.objects.filter(course=course, student=student).exists():
                        enrollment = Enrollment.objects.get(course=course, student=student)
                except Student.DoesNotExist:
                    pass

        content = {
            'course': course,
            'enrollment': enrollment,
            'overview':overview,
            'message': 'FOUND' if enrollment else 'NOT_FOUND',
        }
        return render(request,template_name='course/certificate.html',context=content)
    
