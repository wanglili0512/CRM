from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

# from rbac import models
from rbac.models import User, Role, Permission

# 权限分配
def distribute_permissions(request):
    """
    分配权限
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    user = User.objects.filter(id=uid)
    rid = request.GET.get('rid')

    # 点击角色处的‘保存’按钮，即为用户修改角色
    if request.method == 'POST' and request.POST.get('postType') == 'role':
        r_lst = request.POST.getlist("roles")   # r_lst 为用户在页面勾选的角色id列表
        user.first().roles.set(r_lst)   # 为用户设置新的角色（set表是先清空，再设置）

    # 点击权限处的‘保存’，即为角色修改权限
    if request.method == 'POST' and request.POST.get('postType') == 'permission':
        p_lst = request.POST.getlist("permissions_id")   # p_lst 是用户提交的权限id列表
        Role.objects.filter(pk=rid).first().permissions.set(p_lst)   # 为角色设置新的权限（先清空，再设置）

    user_list = User.objects.all()       # 查询所有用户
    role_list = Role.objects.all()       # 查询所有角色

    if uid:   # 如果url中有用户id，即uid存在，说明用户点击了某用户
        role_id_list= User.objects.get(pk=uid).roles.all().values_list("pk")
        role_id_list = [item[0] for item in role_id_list]

        if rid:
            per_id_list = Role.objects.filter(pk=rid).values_list("permissions__pk").distinct()
        else:
            per_id_list = User.objects.get(pk=uid).roles.values_list("permissions__pk").distinct()
        per_id_list = [item[0] for item in per_id_list]

    return render(request, 'distribute_permission.html', locals())


def permissions_tree(request):
    permissions = Permission.objects.values("pk", "title", "url", "menu__title", "menu__pk", "pid_id")
    print("permissions---------", permissions)
    return JsonResponse(list(permissions), safe=False)   # 将查询到的QuerySet进行序列化，非字典类型序列化时加safe=False
