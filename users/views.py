from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    get_user_model,
    logout,
)
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from django.contrib import messages

# يفترض أنك تستخدم نموذج تسجيل الدخول الخاص بك، إذا لم يكن هذا هو الحال، قم بتعديله حسب الحاجة
from accounts.forms import UserLoginForm, UserRegisterForm

User = get_user_model()

def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('/home/')
    return render(request, "webapp/form.html", {"form": form, "title": title})

# للتسجيل
class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'webapp/registration_form.html'

    # عرض نموذج فارغ
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # معالجة بيانات النموذج
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # تنظيف البيانات
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.save()

            # يعيد كائن المستخدم إذا كانت بيانات الاعتماد صحيحة
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home/')
        return render(request, self.template_name, {'form': form})

def logout_view(request):
    title = 'Logout'
    logout(request)
    return render(request, "webapp/logout.html", {'title': title})

# إضافة طريقة عرض تسجيل الخروج المخصصة
class CustomLogoutView(LogoutView):
    """
    طريقة عرض تسجيل الخروج المخصصة التي تعيد توجيه المستخدم إلى الصفحة الرئيسية بعد تسجيل الخروج
    """
    next_page = reverse_lazy('webapp:index')  # توجيه المستخدم إلى الصفحة الرئيسية بعد تسجيل الخروج
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have successfully logged out.')
        return super().dispatch(request, *args, **kwargs)