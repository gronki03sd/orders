from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from stats.utils import get_dashboard_stats, get_monthly_sales_data

@login_required
def dashboard_view(request):
    """Dashboard view - requires login"""
    stats_data = get_dashboard_stats()
    
    # حساب عدد المنتجات بمخزون عادي
    normal_stock_count = stats_data['total_products'] - stats_data['low_stock_count']
    
    # الحصول على بيانات المبيعات الشهرية
    monthly_sales = get_monthly_sales_data()
    
    # تغيير أسماء الأشهر للإنجليزية بشكل صريح
    english_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_sales['labels'] = english_months
    
    context = {
        'title': 'Dashboard',
        'stats': stats_data,
        'sales_data': monthly_sales,
        'normal_stock_count': normal_stock_count
    }
    return render(request, 'dashboard/index.html', context)