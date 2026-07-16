from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _

# User = get_user_model()


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
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )

    # class Meta(UserCreationForm.Meta):
    #     model = User
    #     fields = ("username", "email")

    def init(self, args, *kwargs):
        super().init(args, *kwargs)
        placeholders = {
            "username": "Имя пользователя",
            "password1": "Пароль",
            "password2": "Повторите пароль",
        }
        autocompletes = {
            "username": "username",
            "password1": "new-password",
            "password2": "new-password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            if name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[name]
            if name in autocompletes:
                field.widget.attrs["autocomplete"] = autocompletes[name]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email
