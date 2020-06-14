from django.shortcuts import render, Http404, HttpResponse, get_object_or_404, redirect
from .models import author, category, article, comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import createForm, registerUser, createAuthor, commentForm, categoryForm
from django.contrib import messages
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from .token import activation_token


# Create your views here.
class index(View):
    def get(self, request):
        post = article.objects.all()

        # start for search..................................
        search = request.GET.get('q')
        if search:
            post = post.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
            # end search...................................

        # start for pagination
        paginator = Paginator(post, 4)  # Show 25 contacts per page.

        page_number = request.GET.get('page')
        total_article = paginator.get_page(page_number)
        # end pagination

        context = {
            "post": total_article
        }

        return render(request, "index.html", context)


# class based view................
class getauthor(View):
    def get(self, request, name):
        post_author = get_object_or_404(User, username=name)
        auth = get_object_or_404(author, name=post_author.id)
        post = article.objects.filter(article_author=auth.id)
        context = {
            "auth": auth,
            "post": post
        }
        return render(request, "profile.html", context)


# funtion based view..........
def getsingle(request, id):
    post = get_object_or_404(article, pk=id)
    first = article.objects.first()
    last = article.objects.last()
    getComment = comment.objects.filter(post=id)
    related = article.objects.filter(category=post.category).exclude(id=id)[:4]  # getting all post to show related post
    form = commentForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.post = post
        instance.save()
    context = {
        "post": post,
        "first": first,
        "last": last,
        "related": related,
        "form": form,
        "comment": getComment
    }

    return render(request, "single.html", context)


def getTopic(request, name):
    cat = get_object_or_404(category, name=name)
    post = article.objects.filter(category=cat.id)
    paginator = Paginator(post, 4)  # Show 25 topic per page.

    page_number = request.GET.get('page')
    total_article = paginator.get_page(page_number)
    return render(request, "category.html", {"post": total_article, "cat": cat})


def getLogin(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('password')
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('index')
            else:
                messages.add_message(request, messages.ERROR, 'Username or Password mismatched')

    return render(request, "login.html")


def getlogout(request):
    logout(request)
    return redirect('index')


def getcreate(request):
    if request.user.is_authenticated:
        u = get_object_or_404(author, name=request.user.id)
        form = createForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.article_author = u
            instance.save()
            return redirect('index')
        return render(request, 'create.html', {"form": form})

    else:
        return redirect('login')


def getProfile(request):
    if request.user.is_authenticated:
        u = get_object_or_404(User, id=request.user.id)
        author_profile = author.objects.filter(name=u.id)
        if author_profile:
            authorUser = get_object_or_404(author, name=request.user.id)
            post = article.objects.filter(article_author=authorUser.id)
            user = get_object_or_404(author, name=request.user.id)
            return render(request, 'logged_in_profile.html', {"post": post, "user": authorUser})
        else:
            form = createAuthor(request.POST or None, request.FILES or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.name = u
                instance.save()
                return redirect('profile')
            return render(request, 'createAuthor.html', {"form": form})

    else:
        return redirect('login')


def getUpdate(request, pid):
    if request.user.is_authenticated:
        u = get_object_or_404(author, name=request.user.id)
        post = get_object_or_404(article, id=pid)
        form = createForm(request.POST or None, request.FILES or None, instance=post)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.article_author = u
            instance.save()
            messages.success(request, 'Article is successfully updated')
            return redirect('profile')

        return render(request, 'create.html', {"form": form})

    else:
        return redirect('login')


def getDelete(request, pid):
    if request.user.is_authenticated:

        post = get_object_or_404(article, id=pid)
        post.delete()
        messages.success(request, 'Article is successfully deleted')
        return redirect('profile')
    else:
        return redirect('login')


def getRegister(request):
    form = registerUser(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.is_active = False
        instance.save()
        site = get_current_site(request)
        mail_subject = "Confirmation message for blog"
        message = render_to_string('confirm_email.html', {
            "user": instance,
            'domain': site.domain,
            'uid': instance.id,
            'token': activation_token.make_token(instance)
        })
        to_email = form.cleaned_data.get('email')
        to_list = [to_email]
        from_email = settings.EMAIL_HOST_USER
        send_mail(mail_subject, message, from_email, to_list, fail_silently=True)
        return HttpResponse("<h1>Thanks for your registration. A confirmation link was sent to your email</h1>")

    return render(request, 'register.html', {"form": form})


def getCategory(request):
    query = category.objects.all()

    return render(request, 'topicsByCategory.html', {"topic": query})


def createCategory(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            form = categoryForm(request.POST or None)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.save()
                messages.success(request, 'Category is successfully created')
                return redirect('category')
            return render(request, 'create_topics.html', {"form": form})
        else:
            raise Http404("You are not permitted")

    else:
        return redirect('login')


def activate(request, uid, token):
    try:
        user = get_object_or_404(User, pk=uid)
    except:
        raise Http404("No user found")
    if user is not None and activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        return HttpResponse("<h1> Account is activated. Now you can <a href='/login'>Login</a>")
    else:
        return HttpResponse("<h3> Invalid activation link")
