from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType  # need to comments when don't using commentmanager
from django.utils import timezone
from django.db.models import Q

from comments.models import Comment
from comments.forms import CommentForm

from .models import Post
from .forms import PostForm
from .utils import get_read_time


def post_list(request):
    today = timezone.now()
    queryset_list = Post.objects.all()  # .order_by('-timestamp')
    if not request.user.is_staff or not request.user.is_superuser:
        queryset_list = Post.objects.filter(publish__lte=timezone.now()).filter(draft=False)
        # lte = LESS THAN or EQUAL
    new_query = request.GET.get('q')
    if new_query:
        queryset_list = Post.objects.filter(
            Q(title__icontains=new_query) |
            Q(content__icontains=new_query)
            # Q(user__icontains=new_query)  # not working
            # todo think how to search user by nick - not only first_name / last_name
        )
    paginator = Paginator(queryset_list, 10)  # Show 10 contacts per page
    page_request_var = 'page'
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
        'object_list': queryset,  # 'nazwa' jest queryset'em O.o
        'title': 'List',  # 'title': 'Nasza_nazwa'
        'page_request_var': page_request_var,
        'today': today,
    }
    return render(request, "posts/post_list.html", context)


def post_detail(request, slug=None):
    today = timezone.now()
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404("You have no permission!")
    # comments = Comment.objects.filter_by_instance(instance)

    # print(get_read_time(instance.content))
    print(get_read_time(instance.get_markdown()))

    initial_data = {
        'content_type': instance.get_content_type,
        'object_id': instance.id,
    }
    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid():
        c_type = comment_form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = comment_form.cleaned_data.get("object_id")
        content_data = comment_form.cleaned_data.get("content")

        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()  # [0]

        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
            content=content_data,
            parent=parent_obj,
        )

        if created:
            print("Yeah!")
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
    comments = instance.comments

    context = {
        'title': instance.title,
        'instance': instance,
        'today': today,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, "posts/post_detail.html", context)


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404("You have no permission!")
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, 'Successfully Created')
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.error(request, 'Not Successfully Created')
    context = {
        'MyForm': form,
    }
    return render(request, "posts/post_form.html", context)


def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404("You have no permission!")
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, 'Saved!')
        return HttpResponseRedirect(instance.get_absolute_url())
        # return HttpResponseRedirect(reverse('detail', args=(instance.id,)))  # args to jest liczba xD
    context = {
        'title': instance.title,
        'instance': instance,
        'MyForm': form,
    }
    return render(request, "posts/post_form.html", context)


def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404("You have no permission!")
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, 'Deleted!')
    return redirect('list')


