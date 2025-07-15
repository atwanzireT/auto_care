from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        user = form.save()
        from django.contrib.auth import login
        login(self.request, user)
        return super().form_valid(form)

