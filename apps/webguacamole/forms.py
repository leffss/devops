from django import forms


class HostForm(forms.Form):
    hostid = forms.IntegerField(label="主机id")
