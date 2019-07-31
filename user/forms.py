from django import forms


class LoginForm(forms.Form):
    # captcha = CaptchaField(error_messages={"invalid": "验证码错误"})
    username = forms.CharField(label="用户名", min_length=1, max_length=64)
    password = forms.CharField(label="密码", min_length=6, max_length=256, widget=forms.PasswordInput)
    
    # class Meta:
    #    model = User
    #    fields = ['name', 'email', 'url', 'text', 'captcha']


class ChangePasswdForm(forms.Form):
    oldpasswd = forms.CharField(label="当前密码", min_length=6, max_length=256, widget=forms.PasswordInput)
    newpasswd = forms.CharField(label="新密码", min_length=6, max_length=256, widget=forms.PasswordInput)
    newpasswdagain = forms.CharField(label="确认新密码", min_length=6, max_length=256, widget=forms.PasswordInput)
