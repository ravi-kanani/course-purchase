from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .models import Topic, Course, Student, Order
from .forms import SearchForm, OrderForm, ReviewForm, RegisterForm, ForgotPasswordForm, ImageUploadForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

class Index(View):
    def get(self, request):
        top_list = Topic.objects.all().order_by('id')[:10]
        return render(request, 'myapp/index.html', {'top_list': top_list, 'last_login': request.session.get('last_login', False)})

def about(request):
    visits=request.COOKIES.get('about_visits')
    if visits:
        visits=int(visits)+1
    else:
        visits=1
    response = render(request, 'myapp/about.html',{'visits': visits})
    response.set_cookie('about_visits', visits, expires=300)
    return response

class Detail(View):
    def get(self, request, topic_id):
        topic=get_object_or_404(Topic,pk=topic_id)
        return render(request, 'myapp/detail.html', {'topic': topic})

def findcourses(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            length = form.cleaned_data['length']
            max_price = form.cleaned_data['max_price']
            courselist = Course.objects.filter(price__lte = max_price)
            if length:
                courselist = courselist.filter(topic__length = length)

            return render(request, 'myapp/results.html', {'courselist':courselist, 'name':name, 'length':length})
        else:
            return HttpResponse('Invalid data')
    else:
        form = SearchForm()
        return render(request, 'myapp/findcourses.html', {'form':form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['courses']
            order = form.save()
            student = order.student
            # courses = order.courses
            status = order.order_status
            order.save()
            if status == 1:
                for c in order.courses.all():
                    student.registered_courses.add(c)
            return render(request, 'myapp/order_response.html', {'courses': courses, 'order':order})
        else:
            return render(request, 'myapp/place_order.html', {'form':form})

    else:
        form = OrderForm()
        return render(request, 'myapp/place_order.html', {'form':form})

def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            if(rating < 1 or rating > 5):
                form.add_error('rating', 'You must enter a rating between 1 and 5!')
                return render(request, 'myapp/review.html', {'form': form})
            review = form.save()
            review.course.num_reviews+=1
            review.course.save()
            return redirect('myapp:index')
        else:
            return render(request, 'myapp/review.html', {'form': form})
    else:
        if (not request.user):
            return render(request, 'myapp/error.html', {'error': 'You must be logged in to submit a review'})
        try:
            user = Student.objects.get(id=request.user.id)
        except Student.DoesNotExist:
            user = None

        if (not user):
            return render(request, 'myapp/error.html', {'error': 'Only students can submit a review'})

        if(user.level=='UG' or user.level=='PG'):
            form = ReviewForm()
            return render(request, 'myapp/review.html', {'form': form})
        return render(request, 'myapp/error.html', {'error': 'Only Undergraduate student or Postgraduate student can submit a review'})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                request.session['last_login'] = str(timezone.now().isoformat('T', 'seconds'))
                request.session.set_expiry(3600)
                return HttpResponseRedirect(reverse('myapp:myaccount'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(('myapp:index')))

@login_required(login_url='/myapp/login')
def myaccount(request):
    if(request.user.is_staff):
        return render(request, 'myapp/myaccount.html', {"is_student": False})
    user = Student.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user.student_image = form.cleaned_data.get('student_image')
            user.save()
    form = ImageUploadForm()
    return render(request, 'myapp/myaccount.html', {"is_student": True, 'form': form, "name":user, 'student_image': user.student_image, "courses":user.registered_courses.all(), "interested_in": user.interested_in.all()})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['registered_courses']
            topics = form.cleaned_data['interested_in']

            student = form.save(commit=False)
            student.set_password(form.cleaned_data['password1'])

            student.save()
            rg = student.registered_courses
            it = student.interested_in
            for t in topics:
                it.add(t)

            for c in courses:
                rg.add(c)

            form.save()
            return redirect('myapp:login')
        else:
            return render(request, 'myapp/register.html', {'form':form})
    else:
        form = RegisterForm()
        return render(request, 'myapp/register.html', {'form': form})

@login_required
def myorders(request):
    try:
        currentUser = Student.objects.get(id=request.user.id)
    except Student.DoesNotExist:
        currentUser = None

    if currentUser:
        orders = Order.objects.filter(student=currentUser).all()
        if orders:
            coursesInOrder = [o.courses.all() for o in orders]
            odate = orders.values_list('order_date', flat=True)
            status = orders.values_list('order_status', flat=True)

            iterableOrders = zip(coursesInOrder, odate, status)

            return render(request, 'myapp/myorders.html', {'orders':iterableOrders })
        else:
            message = "You don't have any orders!"
            return render(request, 'myapp/myorders.html', {'message':message })
    else:
        message = "You Are Not a Registered Student"
        return render(request, 'myapp/myorders.html', {'message': message })

def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                student = Student.objects.get(username=username)
                new_pwd = student.username + "1234"
                student.set_password(new_pwd)
                student.save()
                send_from = 'ravikanani280@gmail.com'
                sent_to = student.email
                mail_content = "Your new password is: " + new_pwd
                send_mail('New Password', mail_content, send_from, [sent_to], fail_silently=False)

                success_message = "New password sent to your email id."
                return render(request, 'myapp/forgot_password.html', {'form': form, 'success_message': success_message})
            except Student.DoesNotExist:
                form= ForgotPasswordForm()
                error_message = 'Invalid Username, Try Again.'
                return render(request, 'myapp/forgot_password.html', {'form': form, 'error_message': error_message})
    else:
        form = ForgotPasswordForm()
        return render(request, 'myapp/forgot_password.html', {'form': form})