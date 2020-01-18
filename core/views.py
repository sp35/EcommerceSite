from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, View, ListView, DetailView
from django.contrib import messages
from core.models import Item, OrderItem, Order, WishList
from users.models import Customer, Vendor
from core.forms import AddMoneyForm, OrderForm
import xlsxwriter
from io import BytesIO


@login_required
def home(request):
    if request.user.is_vendor:
        items = Item.objects.filter(vendor=Vendor.objects.get(user=request.user))
        return render(request, "core/vendor_home.html", {'items': items})
    elif request.user.is_customer:
        items = Item.objects.all()
        wallet = Customer.objects.get(user=request.user).wallet
        return render(request, "core/customer_home.html", {'items': items, 'wallet': wallet})
    return redirect('login')


class AddMoneyFormView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = AddMoneyForm
    template_name = 'core/add_money.html'

    def test_func(self):
        if self.request.user.is_customer:
            return True
        return False

    def get(self, request):
        form = self.form_class()
        customer = Customer.objects.get(user=request.user)
        return render(request, self.template_name, {'form': form, 'wallet': customer.wallet})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            customer = Customer.objects.get(user=request.user)
            customer.wallet += form.cleaned_data['money']
            customer.save()
        return render(request, self.template_name, {'form': form, 'wallet': customer.wallet})


class ItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Item
    fields = [ 'title', 'image', 'price', 'description', 'units_available' ]

    def test_func(self):
        if self.request.user.is_vendor:
            return True
        return False

    def form_valid(self, form):
        vendor = Vendor.objects.get(user=self.request.user)
        form.instance.vendor = vendor
        return super(ItemCreateView, self).form_valid(form)


class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    success_url = '/'

    def test_func(self):
        item = self.get_object()
        if self.request.user.is_vendor and self.request.user == item.vendor.user:
            return True
        return False


class OrderItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OrderItem
    fields = [ 'quantity' ]
    success_url = '/'

    def test_func(self):
        if self.request.user.is_customer:
            return True
        return False

    def form_valid(self, form):
        customer = Customer.objects.get(user=self.request.user)
        item = Item.objects.get(pk=self.kwargs['pk'])
        form.instance.customer = customer
        form.instance.item = item
        form.instance.vendor = item.vendor
        return super(OrderItemCreateView, self).form_valid(form)


class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Order
    fields = [ 'items' ]
    success_url = '/'

    def test_func(self):
        if self.request.user.is_customer:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        context['customer_id'] = Customer.objects.get(user=self.request.user).pk
        return context

    def get_form(self, *args, **kwargs):
        form = super(OrderCreateView, self).get_form(*args, **kwargs)
        form.fields['items'].queryset = OrderItem.objects.filter(ordered=False)
        return form

    def form_valid(self, form):
        customer = Customer.objects.get(user=self.request.user)
        if customer.wallet < form.instance.items.item.price:
            messages.warning(self.request, 'Insufficient Wallet Balance')
            return super(OrderCreateView, self).form_invalid(form)
        elif not form.instance.items.item.units_available:
            messages.warning(self.request, 'Item out of stock')
            return super(OrderCreateView, self).form_invalid(form)
        elif customer.address is None:
            messages.warning(self.request, 'Address not provided')
            return super(OrderCreateView, self).form_invalid(form)
        form.instance.customer = customer
        form.instance.items.ordered = True
        form.instance.items.item.sales += form.instance.items.quantity
        form.instance.items.save()
        form.instance.items.item.save()
        customer.wallet -= form.instance.items.item.price
        customer.save()
        return super(OrderCreateView, self).form_valid(form)


@login_required
def order(request):
    if not request.user.is_customer:
        return PermissionDenied()
    customer = Customer.objects.get(user=request.user)
    if request.method == 'POST':
        issues = False
        total_amount = 0
        form = OrderForm(request.POST)
        if form.is_valid():
            for order_items in form.cleaned_data['order_items']:
                total_amount += order_items.item.price
                if not order_items.item.units_available:
                    messages.warning(request, 'Item out of stock')
                    issues = True
                    break
        if not issues:
            if customer.wallet < total_amount:
                messages.warning(request, 'Insufficient Wallet Balance')
                issues = True
            elif customer.address is None:
                messages.warning(request, 'Address not provided')
                issues = True
        if not issues:
            form.instance.customer = customer
            for order_items in form.cleaned_data['order_items']:
                order_items.ordered = True
                order_items.item.sales += order_items.quantity
                order_items.save()
                order_items.item.save()
            customer.wallet -= total_amount
            customer.save()
            form.save()
            return redirect('home')
        else:
            form = OrderForm()
            form.fields['order_items'].queryset = OrderItem.objects.filter(ordered=False)

    else:
        form = OrderForm()
        form.fields['order_items'].queryset = OrderItem.objects.filter(ordered=False)

    return render(request, 'core/order_form.html', { 'customer_id': customer.pk, 'form': form })


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = 'orders'

    def get_queryset(self):
        if self.request.user.is_customer:
            return Order.objects.filter(customer=Customer.objects.get(user=self.request.user))
        elif self.request.user.is_vendor:
            return Order.objects.filter(
                order_items__in=OrderItem.objects.filter(
                    vendor=Vendor.objects.get(user=self.request.user)))


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order


@login_required
def generate_sales_report(request):
    if not request.user.is_vendor:
        return PermissionDenied()
    items = Item.objects.filter(vendor=Vendor.objects.get(user=request.user)).values_list('title', 'sales')

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    row = col= 0
    for title, sales in items:
        worksheet.write(row, col, title)
        worksheet.write(row, col + 1, sales)
        row += 1
    workbook.close()
    # create a response
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    response['Content-Disposition'] = 'attachment;filename="sales_report.xlsx"'
    # put the spreadsheet data into the response
    response.write(output.getvalue())
    return response


@login_required
def wish_list(request, pk):
    if not request.user.is_customer:
        return PermissionDenied()
    item = Item.objects.get(pk=pk)
    WishList.objects.get_or_create(item=item, customer=Customer.objects.get(user=request.user))
    messages.success(request, "Added to Wishlist")

    return redirect('home')