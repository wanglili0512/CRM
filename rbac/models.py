from django.db import models
# Create your models here.

class User(models.Model):
    """
    用户表
    """
    name = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role')

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    角色表
    """
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission')

    def __str__(self):
        return self.title


class Permission(models.Model):
    """
    权限表
    """
    url = models.CharField(verbose_name='含正则的URL', max_length=32)
    title = models.CharField(verbose_name='标题', max_length=32)
    menu = models.ForeignKey(verbose_name='标题', to="Menu", on_delete=models.CASCADE, null=True)
    name = models.CharField(verbose_name='url别名', max_length=32, default="")
    pid = models.ForeignKey("self", on_delete=models.CASCADE, null=True, verbose_name='父权限')

    def __str__(self):
        return self.title


class Menu(models.Model):
    """
    菜单表
    """
    title = models.CharField(max_length=32, verbose_name='菜单')
    icon = models.CharField(max_length=32, verbose_name='图标', null=True, blank=True)