from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginUserForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control login-input",
                "placeholder": "you@example.com",
                "autofocus": True,
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label=_("password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control login-input",
                "placeholder": "Пароль",
                "autocomplete": "current-password",
            }
        ),
    )
    error_messages = {
        "invalid_login": _("Неверный Email или пароль"),
        "inactive": _("Этот аккаунт отключён"),
    }


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control login-input",
                    "placeholder": "you@example.com",
                    "autofocus": True,
                    "autocomplete": "email",
                }
            ),
        }

    def init(self, args, *kwargs):
        super().init(args, *kwargs)
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control login-input",
                "autocomplete": "new-password",
                "placeholder": "Пароль",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control login-input",
                "autocomplete": "new-password",
                "placeholder": "Повторите пароль",
            }
        )
        self.fields["password2"].label = _("Подтверждение пароля")


class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "city",
            "street",
            "house_number",
            "apartment_number",
            "postal_code",
        ]
