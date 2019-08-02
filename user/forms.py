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


class ChangeUserProfileForm(forms.Form):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    nickname = forms.CharField(label="昵称", max_length=64)
    email = forms.EmailField(label="邮箱")
    phone = forms.CharField(label="手机", min_length=11, max_length=11, required=False)
    weixin = forms.CharField(label="微信", max_length=64, required=False)
    qq = forms.CharField(label="QQ", max_length=64, required=False)
    sex = forms.ChoiceField(label="性别", choices=SEX_CHOICES)
    memo = forms.CharField(label="昵称", max_length=256, widget=forms.Textarea, required=False)


class ChangeUserForm(forms.Form):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    ROLE_CHOICES = (
        (1, '超级管理员'),
        (2, '普通用户'),
    )
    username = forms.CharField(label="用户名", max_length=64)
    nickname = forms.CharField(label="昵称", max_length=64)
    email = forms.EmailField(label="邮箱")
    phone = forms.CharField(label="手机", min_length=11, max_length=11, required=False)
    weixin = forms.CharField(label="微信", max_length=64, required=False)
    qq = forms.CharField(label="QQ", max_length=64, required=False)
    sex = forms.ChoiceField(label="性别", choices=SEX_CHOICES)
    memo = forms.CharField(label="昵称", max_length=256, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="是否启用", required=False)
    role = forms.ChoiceField(label="角色", choices=ROLE_CHOICES)
    groups = forms.CharField(label="用户组", max_length=10240, required=False)
    
