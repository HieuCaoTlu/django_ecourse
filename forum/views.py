from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from forum.models import Post, Reply, Like
from django.http import HttpResponse, Http404, HttpResponseRedirect
from base.models import Student, User
from .form import PostForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class HomepageForum(View):

    def get(self, request):
        # Lấy ra các bài đăng và sắp xếp theo thời gian tạo mới nhất
        all_posts = Post.objects.order_by('-created_at')

        # Thêm thuộc tính cho mỗi bài đăng
        for each in all_posts:
            each.is_student = hasattr(each.user,'student')
            each.content_hidden = f'{each.content[:75]}..'
            each.gender = each.user.gender
            each.reply_count = Reply.objects.filter(post=each).count()

        # Phân trang
        paginator = Paginator(all_posts, 5)
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        # Truyền dữ liệu cho template
        is_logged_in = request.user.is_authenticated
        context = {'posts': posts, 'is_logged_in': is_logged_in}
        return render(request, template_name='forum/homepage.html', context=context)

class DetailPost(View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        form = PostForm(instance=post)
        replies = Reply.objects.filter(post=post).order_by('-created_at')
        post.reply_count = replies.count()
        is_owner = request.user == post.user
        return render(request, 'forum/detail.html', {'post': post, 'replies': replies, 'form': form, 'is_owner': is_owner, 'is_student': hasattr(post.user, 'student')})

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        
        if request.POST.get('delete') == 'True':
            if request.user == post.user:
                post.delete()
                return redirect('forum:homepage')
            else:
                raise Http404("You are not authorized to delete this post.")
        elif request.POST.get('edit') == 'True':
            if request.user == post.user:
                form = PostForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    return HttpResponse("<script>alert('Đã chỉnh sửa bài đăng');history.back()</script>")
                else:
                    pass
            else:
                return redirect('forum:post',post_id=post.id)
        else:
            reply = Reply()
            reply.content = request.POST.get('content')
            reply.user = request.user
            reply.post = post
            reply.save()
            return redirect('forum:post',post_id=post.id)

def makingpost(request):
    if request.method == "POST":
        post = Post()
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.user = request.user
        post.save()
        return redirect("forum:post", post.id)
    return render(request, 'forum/addpost.html')

def like_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)

        if user in post_obj.likes.all():
            post_obj.likes.remove(user)
        else:
            post_obj.likes.add(user)
        
        like, created = Like.objects.get_or_create(user=user, post=post_obj)
        if not created:
            like.value = 'Unlike' if like.value == 'Like' else 'Like'
            like.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        pass
