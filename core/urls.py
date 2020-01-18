from django.urls import path
from core import views as core_views


urlpatterns = [
    path('', core_views.home, name='home'),
    path('item/new', core_views.ItemCreateView.as_view(), name='item-create'),
    path('item/<int:pk>/delete/', core_views.ItemDeleteView.as_view(), name='item-delete'),
    path('add_money/', core_views.AddMoneyFormView.as_view(), name='add-money'),
    path('orderitem/new/item/<int:pk>', core_views.OrderItemCreateView.as_view(), name='order-item-create'),
    # path('order/new', core_views.OrderCreateView.as_view(), name='order-create'),
    path('order/new', core_views.order, name='order-create'),
    path('order/<int:pk>/detail', core_views.OrderDetailView.as_view(), name='order-detail'),
    path('ordered/', core_views.OrderListView.as_view(), name='ordered-list'),
    path('wish_list/item/<int:pk>', core_views.wish_list, name='wish_list'),
    path('generate_sales_report', core_views.generate_sales_report, name='generate_sales_report'),
]