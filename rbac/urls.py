from django.urls import path, re_path

from rbac import views

urlpatterns = [
    # 6. 权限管理

    # 分配权限按钮
    re_path(r'^distribute/permissions/$', views.distribute_permissions, name="distribute_permissions"),

    # 权限分配按钮加载后自动发送ajax请求权限树
    re_path(r'^permissions_tree/$', views.permissions_tree, name="permissions_tree"),
]

