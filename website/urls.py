from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# استيراد طرق العرض المحددة
from users.views import CustomLogoutView  # تأكد من أن هذا الاستيراد صحيح ومتوافق مع هيكل المشروع الخاص بك

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('webapp.urls')),  # يتضمن المسارات من تطبيق webapp
    path('accounts/', include('accounts.urls')),  # يتضمن المسارات من تطبيق accounts
    path('logout/', CustomLogoutView.as_view(), name='logout'),  # مسار تسجيل الخروج المخصص
]

# إضافة مسارات الملفات الثابتة في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)