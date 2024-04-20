from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, default='')
    CHOICE = (
        (0, 'Nam'),    
        (1, 'Nữ'),    
        (2, 'Không biết'),    
    )
    gender = models.IntegerField(choices=CHOICE, default=0)
    birth_date = models.DateField(blank=True, null=True)
    date_assign = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

class Teacher(User):
    CHOICE = (
        (0, 'Giảng viên'),    
        (1, 'Thạc Sĩ'),    
        (2, 'Tiến sĩ'),    
    )
    level = models.IntegerField(choices=CHOICE, default=0)
    earning = models.IntegerField(default=0, blank=True)
    class Meta:
        verbose_name = 'Giảng viên'
        verbose_name_plural = 'Giảng viên'


class Student(User):
    CHOICE = (
        (0, 'Trí tuệ nhân tạo'),    
        (1, 'Công nghệ thông tin'),    
        (2, 'Khoa học máy tính'),    
        (4, 'Ngành khác'),    
    )
    major = models.IntegerField(choices=CHOICE, default=0)

    class Meta:
        verbose_name = 'Học viên'
        verbose_name_plural = 'Học viên'


class Material(models.Model):
    title = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        verbose_name = 'Chất liệu'
        verbose_name_plural = 'Chất liệu'


    def __str__(self):
        return f"{self.title}"
    
class Category(models.Model):
    title = models.CharField(max_length=15, default='')
    level = models.CharField(max_length=20, default='')
    image = models.ImageField(upload_to='category/', blank=True, null=True)
    cover = models.URLField(default='')

    def __str__(self):
        return f"{self.title} {self.level}"
    
    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'


class Course(Material):
    cover = models.URLField(default='')
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    price = models.IntegerField(default=0,blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    active = models.BooleanField(default=False,blank=True)

    class Meta:
        verbose_name = 'Khóa học'
        verbose_name_plural = 'Khóa học'

    
class Section(Material):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Phần học'
        verbose_name_plural = 'Phần học'

    
class Lesson(Material):
    CHOICE = (
        ('PDF', 'PDF'),
        ('VIDEO', 'Video'),
        ('MEET', 'Meet')
    )
    document_type = models.CharField(max_length=5, choices=CHOICE)
    document = models.URLField(default='')
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Bài học'
        verbose_name_plural = 'Bài học'


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    vote = models.IntegerField(default=0, blank=True)
    enroll_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0, null=False)
    completed = models.BooleanField(default=False, blank=True)
    review = models.CharField(blank=True, max_length=200)
    certificate = models.URLField(default='', blank=True)

    class Meta:
        unique_together = ['student', 'course']
        verbose_name = 'Ghi danh'
        verbose_name_plural = 'Ghi danh'

    def __str__(self):
        formatted_enroll_date = self.enroll_date.strftime("%Y-%m-%d %H:%M")
        return f"{self.student} - {formatted_enroll_date}"

class LessonProcess(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    bookmark = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tiến trình'
        verbose_name_plural = 'Tiến trình'

    def __str__(self):
        return f"{self.lesson} - {self.enrollment}"


class CourseDescription(models.Model):
    description = models.TextField(default='')
    scope1 = models.CharField(max_length=100, blank=True)
    scope2 = models.CharField(max_length=100, blank=True)
    scope3 = models.CharField(max_length=100, blank=True)
    scope4 = models.CharField(max_length=100, blank=True)
    scope5 = models.CharField(max_length=100, blank=True)
    scope6 = models.CharField(max_length=100, blank=True)
    course = models.OneToOneField(Course, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Mô tả khóa học'
        verbose_name_plural = 'Mô tả'

