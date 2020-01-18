from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import CreateView, TemplateView, UpdateView
from users.forms import CustomerSignUpForm, VendorSignUpForm
from django.conf import settings
from users.models import Customer


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


class CustomerSignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = CustomerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        return redirect('home')


class VendorSignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = VendorSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'vendor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        return redirect('home')


class CustomerUpdateView(UpdateView):
    model = Customer
    fields = [ 'address' ]
    template_name = 'registration/customer_update.html'

    def form_valid(self, form):
        form.save()
        return redirect('home')