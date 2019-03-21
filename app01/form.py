import re

from django import forms
from django.forms import widgets as wid
from django.core.exceptions import ValidationError

from app01.models import UserInfo, Customer, ConsultRecord, Enrollment, ClassStudyRecord, StudentStudyRecord


class UserInfoModelForm(forms.ModelForm):
    r_pwd= forms.CharField(widget=wid.PasswordInput(attrs={"type": "password", "placeholder": "确认密码", "onfocus":"this.placeholder=''", "onblur":"this.placeholder='确认密码'"}),
                           label="&#xe7b8;")
    class Meta:
        model=UserInfo
        fields=["username", "tel", "password", "r_pwd", "email"]
        labels={
            "username": "&#xe623;",
            "tel": "&#xe652;",
            "password": "&#xe7b8;",
            "email": "&#xe7b1;"
        }
        widgets={
            "username": wid.TextInput(attrs={"placeholder": "用户名", "onfocus":"this.placeholder=''", "onblur":"this.placeholder='用户名'"}),
            "tel": wid.TextInput(attrs={"placeholder": "手机号", "onfocus":"this.placeholder=''", "onblur":"this.placeholder='手机号'"}),
            "password": wid.PasswordInput(attrs={"type": "password", "placeholder": "密码", "onfocus":"this.placeholder=''", "onblur":"this.placeholder='密码'"}),
            "email": wid.TextInput(attrs={"placeholder": "邮箱", "onfocus":"this.placeholder=''", "onblur":"this.placeholder='邮箱'"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.error_messages={"required": "该字段不能为空"}

    # 局部钩子- 校验用户名是否存在
    def clean_user(self):
        val = self.cleaned_data.get("username")
        user = UserInfoModelForm.objects.filter(username=val).first()
        if user:
            raise ValidationError("用户已存在！")
        else:
            return val

    # 局部钩子 - 密码校验
    def clean_pwd(self):
        val = self.cleaned_data.get("password")
        if val.isdigit():
            raise ValidationError("密码不能是纯数字！")
        else:
            return val

    # 局部钩子 - 邮箱校验
    # def clean_email(self):
    #     val = self.cleaned_data.get("email")
    #     if re.search(r"\w+@163.com$", val):
    #         return val
    #     else:
    #         raise ValidationError("邮箱必须是163邮箱！")

    # 全局钩子 - 校验密码是否一致
    def clean(self):
        pwd = self.cleaned_data.get("password")
        r_pwd = self.cleaned_data.get("r_pwd")

        if pwd and r_pwd and r_pwd != pwd:
            self.add_error("r_pwd", ValidationError("两次密码不一致！"))
        else:
            return self.cleaned_data


# 添加/编辑客户的表单校验
class CustomerModelForm(forms.ModelForm):
    class Meta:
        model=Customer
        fields="__all__"

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.error_messages = {"required": "该字段不能为空"}


# 添加/编辑跟进记录表单校验
class ConsultRecordModelForm(forms.ModelForm):
    class Meta:
        model=ConsultRecord
        exclude=['delete_status']


# 添加/编辑报名记录表单校验
class EnrollmentModelForm(forms.ModelForm):
    class Meta:
        model=Enrollment
        fields=['customer', 'why_us', 'your_expectation', 'school', 'enrolment_class', 'memo']
        # exclude=['delete_status']

# 添加/编辑班级学习记录表单校验
class CSRecordModelForm(forms.ModelForm):
    class Meta:
        model=ClassStudyRecord
        fields='__all__'

# 添加学生学习记录
class SSRecordModelForm(forms.ModelForm):
    class Meta:
        model=StudentStudyRecord
        fields='__all__'

# 录入成绩校验
class InputSSRecordModelForm(forms.ModelForm):
    class Meta:
        model=StudentStudyRecord
        # fields='__all__'
        fields=['score', 'homework_note']