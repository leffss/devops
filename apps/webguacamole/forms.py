from django import forms


class HostForm(forms.Form):
    hostid = forms.IntegerField(label="主机id")


class SessionViewForm(forms.Form):
    sessionname = forms.CharField(label="会话名称")
    group = forms.CharField(label="会话组")