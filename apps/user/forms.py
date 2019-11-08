from django import forms


class LoginForm(forms.Form):
    # captcha = CaptchaField(error_messages={"invalid": "验证码错误"})
    username = forms.CharField(label="用户名", min_length=1, max_length=64)
    password = forms.CharField(label="密码", min_length=6, max_length=32, widget=forms.PasswordInput)
    
    # class Meta:
    #    model = User
    #    fields = ['name', 'email', 'url', 'text', 'captcha']


class ChangePasswdForm(forms.Form):
    oldpasswd = forms.CharField(label="当前密码", min_length=6, max_length=32, widget=forms.PasswordInput)
    newpasswd = forms.CharField(label="新密码", min_length=6, max_length=32, widget=forms.PasswordInput)
    newpasswdagain = forms.CharField(label="确认新密码", min_length=6, max_length=32, widget=forms.PasswordInput)


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
    memo = forms.CharField(label="备注", max_length=256, widget=forms.Textarea, required=False)
    clissh_name = forms.CharField(label="clissh客户端", max_length=64, required=False)
    clissh_path = forms.CharField(label="clissh程序路径", max_length=512, required=False)
    clissh_args = forms.CharField(label="clissh命令参数", max_length=512, required=False)
    clisftp_name = forms.CharField(label="clisftp客户端", max_length=64, required=False)
    clisftp_path = forms.CharField(label="clisftp程序路径", max_length=512, required=False)
    clisftp_args = forms.CharField(label="clisftp命令参数", max_length=512, required=False)


class ChangeUserForm(forms.Form):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    ROLE_CHOICES = (
        (1, '超级管理员'),
        (2, '普通用户'),
    )
    userid = forms.IntegerField(label="用户ID")
    nickname = forms.CharField(label="昵称", max_length=64)
    email = forms.EmailField(label="邮箱")
    phone = forms.CharField(label="手机", min_length=11, max_length=11, required=False)
    weixin = forms.CharField(label="微信", max_length=64, required=False)
    qq = forms.CharField(label="QQ", max_length=64, required=False)
    sex = forms.ChoiceField(label="性别", choices=SEX_CHOICES)
    memo = forms.CharField(label="备注", max_length=256, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="是否启用", required=False)
    role = forms.ChoiceField(label="角色", choices=ROLE_CHOICES)
    groups = forms.CharField(label="用户组", max_length=102400, required=False)
    hosts = forms.CharField(label="用户拥有主机", max_length=102400, required=False)
    permissions = forms.CharField(label="用户拥有权限", max_length=102400, required=False)

    
class AddUserForm(forms.Form):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    ROLE_CHOICES = (
        (1, '超级管理员'),
        (2, '普通用户'),
    )
    username = forms.CharField(label="用户名", max_length=64)
    newpasswd = forms.CharField(label="新密码", min_length=6, max_length=32, widget=forms.PasswordInput)
    newpasswdagain = forms.CharField(label="确认新密码", min_length=6, max_length=32, widget=forms.PasswordInput)
    nickname = forms.CharField(label="昵称", max_length=64)
    email = forms.EmailField(label="邮箱")
    phone = forms.CharField(label="手机", min_length=11, max_length=11, required=False)
    weixin = forms.CharField(label="微信", max_length=64, required=False)
    qq = forms.CharField(label="QQ", max_length=64, required=False)
    sex = forms.ChoiceField(label="性别", choices=SEX_CHOICES)
    memo = forms.CharField(label="备注", max_length=256, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="是否启用", required=False)
    role = forms.ChoiceField(label="角色", choices=ROLE_CHOICES)
    groups = forms.CharField(label="用户组", max_length=102400, required=False)
    hosts = forms.CharField(label="用户拥有主机", max_length=102400, required=False)
    permissions = forms.CharField(label="用户拥有权限", max_length=102400, required=False)

    
class ChangeGroupForm(forms.Form):
    groupid = forms.IntegerField(label="组ID")
    memo = forms.CharField(label="备注", max_length=256, widget=forms.Textarea, required=False)
    users = forms.CharField(label="组内用户", max_length=102400, required=False)
    hosts = forms.CharField(label="组拥有主机", max_length=102400, required=False)
    permissions = forms.CharField(label="组拥有权限", max_length=102400, required=False)


class AddGroupForm(forms.Form):
    groupname = forms.CharField(label="组名", max_length=64)
    memo = forms.CharField(label="备注", max_length=256, widget=forms.Textarea, required=False)
    users = forms.CharField(label="组内用户", max_length=102400, required=False)
    hosts = forms.CharField(label="组拥有主机", max_length=102400, required=False)
    permissions = forms.CharField(label="组拥有权限", max_length=102400, required=False)
