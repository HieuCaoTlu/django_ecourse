from django.shortcuts import render
from django.views import View

# Create your views here.
class HomepageForum(View):

    def get(self, request):
        return render(request, template_name='forum/base.html',)