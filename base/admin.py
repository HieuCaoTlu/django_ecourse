from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as SystemAdmin
from .models import *
from .forms import *
from django.utils.html import format_html
from django.urls import reverse

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    readonly_fields = ['edit_section_link']

    def edit_section_link(self, obj):
        if obj.id:
            url = reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
            return format_html('<a href="{}">Edit Section</a>', url)
        else:
            return 'Save and continue editing to create the link.'
    edit_section_link.short_description = "Edit Section"

class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ['title','active','category','edit_Course_link']
    readonly_fields = ['edit_Course_link']

    def edit_Course_link(self, obj):
        if obj.id:
            url = reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
            return format_html('<a href="{}">Edit Course</a>', url)
        else:
            return 'Save and continue editing to create the link.'
    edit_Course_link.short_description = "Edit Course"

class CourseDescriptionInline(admin.StackedInline):
    model = CourseDescription

class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    readonly_fields = ('cover',)
    search_fields = ('title',)
    list_display = ('title','active','category','display_teacher','created_at')
    inlines = [CourseDescriptionInline,SectionInline]
    list_filter = ["title","category","active"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if request.user.is_superuser or request.user.groups.filter(name='Operate').exists():
            return qs
        else:
            if request.user.groups.filter(name='Teacher').exists():
                teacher = Teacher.objects.get(pk=request.user.id)
                return qs.filter(teacher=teacher)
            return qs.exclude(active=True)
        
    def display_created(self, obj):
        return f"${obj.created_at}"
    
    def display_teacher(self, obj):
        link = reverse("admin:base_teacher_change", args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', link, obj.teacher)
    
    def get_exclude(self, request, obj=None):
        groups = request.user.groups.all()
        is_teacher = any(group.name == 'Teacher' for group in groups)
        if is_teacher:
            return ['price', 'active']
        return []
        
    display_created.admin_order_field = "created_at"
    display_teacher.short_description = "Giảng viên"

class LessonInLine(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'document_type','edit_lesson_link')
    readonly_fields = ['edit_lesson_link']

    def edit_lesson_link(self, obj):
        if obj.id:
            url = reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
            return format_html('<a href="{}">Edit Lesson</a>', url)
        else:
            return 'Save and continue editing to create the link.'
    edit_lesson_link.short_description = "Edit Lesson"

class SectionAdmin(admin.ModelAdmin):
    model = Section
    inlines = [LessonInLine]

class LessonAdmin(admin.ModelAdmin):
    model = Lesson
    form = LessonAdminForm
    readonly_fields=('document',)

class UserAdmin(SystemAdmin):   
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('full_name', 'is_staff', 'is_active',)
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email', 'phone','first_name', 'last_name','gender','birth_date'),
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name','gender','birth_date','groups'),
        }),
    )
    search_fields = ('last_name',)
    ordering = ('date_assign',)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    full_name.short_description = 'Họ và tên'

class TeacherAdmin(UserAdmin):
    model = Teacher
    form = TeacherChangeForm
    add_form = TeacherCreationForm
    search_fields = ('last_name','first_name')
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('username', 'password', 'email', 'phone','first_name', 'last_name','earning','level'),
        }),
        ('Trạng thái', {
            'fields': ('is_staff', 'is_active',),
        }),
    )
    add_fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name','level'),
        }),
    )
    list_display = ('full_name', 'phone', 'email', 'is_staff',  'is_active')
    inlines = [CourseInline]

    def get_fieldsets(self, request, obj=None):
        finance = Group.objects.get(name='Finance')
        if request.user.is_superuser or request.user.groups.filter(name='Finance').exists():
            return super().get_fieldsets(request, obj)
        else:
            return (
                ('Thông tin cá nhân', {
                    'fields': ('username', 'password', 'email', 'phone', 'first_name', 'last_name', 'level'),
                }),
                ('Trạng thái', {
                    'fields': ('is_active',),
                }),
            )

class ProcessInLine(admin.TabularInline):
    model = LessonProcess
    extra = 0

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ['course','completed','edit_enroll_link']
    readonly_fields = ['edit_enroll_link']

    def edit_enroll_link(self, obj):
        if obj.id:
            url = reverse("admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
            return format_html('<a href="{}">Xem thông tin ghi danh</a>', url)
        else:
            return 'Save and continue editing to create the link.'
    edit_enroll_link.short_description = "Xem thông tin ghi danh"

class StudentAdmin(UserAdmin):
    model = Student
    form = StudentChangeForm
    add_form = StudentCreationForm
    search_fields = ('last_name','first_name')
    fieldsets = (
        ('Thông tin cá nhân', {
            'fields': ('username', 'password', 'email', 'phone', 'first_name', 'last_name','major','gender','birth_date'),
        }),
        ('Trạng thái hoạt động', {
            'fields': ('is_active',),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'major','gender','birth_date'),
        }),
    )
    list_display = ('full_name', 'phone', 'email', 'is_active',)
    inlines = [EnrollmentInline]

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['course', 'student', 'vote', 'enroll_date']
    inlines=[ProcessInLine]

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    readonly_fields = ('cover',)

admin.site.site_title = "Quản lý hệ thống khóa học"
admin.site.site_header = "Hệ thống quản trị viên"
admin.site.index_title = "Trang quản trị"
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(LessonProcess)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(Lesson,LessonAdmin)
admin.site.register(Category, CategoryAdmin)
