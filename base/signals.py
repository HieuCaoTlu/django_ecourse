from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lesson
from .models import Enrollment, LessonProcess

@receiver(post_save, sender=Lesson)
def update_lesson(sender, instance, **kwargs):
    if kwargs.get('created', False):  
        enrollments = Enrollment.objects.filter(course=instance.section.course)
        for enrollment in enrollments:
            LessonProcess.objects.create(enrollment=enrollment, lesson=instance)
