from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from django.views.generic import CreateView, UpdateView

from .forms import LoginUserForm, RegisterUserForm
from apps.orders.models import Order
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ProfileUserForm


class UserLoginView(LoginView):
    template_name = "login.html"
    form_class = LoginUserForm
    redirect_authenticated_user = True
    next_page = reverse_lazy("users:profile")


class RegisterView(CreateView):
    template_name = "register.html"
    form_class = RegisterUserForm
    success_url = reverse_lazy("users:profile")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("users:profile")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUserForm
    template_name = "profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["orders"] = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related(
                "items",
                "items__clothing_item",
                "items__size",
            )
            .order_by("-created_at")
        )
        return context
