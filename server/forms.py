from django import forms


class ChangeUserForm(forms.Form):
    userid = forms.IntegerField(label="用户ID")
    username = forms.CharField(label="用户名", max_length=128)
    password = forms.CharField(label="密码", max_length=512)
    memo = forms.CharField(label="备注", max_length=255, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="登陆后是否su跳转超级用户", required=False)
    superusername = forms.CharField(label="超级用户", max_length=128, required=False)
    superpassword = forms.CharField(label="超级密码", max_length=512, required=False)


class AddUserForm(forms.Form):
    name = forms.CharField(label="名称", max_length=128)
    username = forms.CharField(label="用户名", max_length=128)
    password = forms.CharField(label="密码", max_length=512)
    memo = forms.CharField(label="备注", max_length=255, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="登陆后是否su跳转超级用户", required=False)
    superusername = forms.CharField(label="超级用户", max_length=128, required=False)
    superpassword = forms.CharField(label="超级密码", max_length=512, required=False)


class ChangeHostForm(forms.Form):
    hostid = forms.IntegerField(label="主机ID")
    type = forms.IntegerField(label="类型")
    ip = forms.GenericIPAddressField(label="主机IP")
    wip = forms.GenericIPAddressField(label="公网IP", required=False)
    protocol = forms.IntegerField(label='协议')
    env = forms.IntegerField(label='环境')
    port = forms.IntegerField(label='端口')
    release = forms.CharField(label="系统/型号", max_length=255)
    memo = forms.CharField(label="备注", max_length=255, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="是否启用", required=False)
    binduserid = forms.IntegerField(label="绑定账号")


class AddHostForm(forms.Form):
    hostname = forms.CharField(label="主机名", max_length=128)
    type = forms.IntegerField(label="类型")
    ip = forms.GenericIPAddressField(label="主机IP")
    wip = forms.GenericIPAddressField(label="公网IP", required=False)
    protocol = forms.IntegerField(label='协议')
    env = forms.IntegerField(label='环境')
    port = forms.IntegerField(label='端口')
    release = forms.CharField(label="系统/型号", max_length=255)
    memo = forms.CharField(label="备注", max_length=255, widget=forms.Textarea, required=False)
    enabled = forms.BooleanField(label="是否启用", required=False)
    binduserid = forms.IntegerField(label="绑定账号")

