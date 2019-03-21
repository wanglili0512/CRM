from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, HttpResponse
import re

from rbac.models import Permission

class PermissionMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        # 设置白名单放行
        for reg in ["/login/", "/admin/*", "/get_identifyCode/", "/logout/", "/rbac/permissions_tree/"]:
            ret = re.search(reg, request.path)
            if ret:
                return None

        # 检验是否登录
        user_id = request.session.get('user_id')     # 用户登录成功则将用户id注入session
        if not user_id:
            return redirect('/login/')

        # 检验权限
        permission_list = request.session.get('permission_list')

        # 路径导航列表
        request.breadcrumb = [
            {
                "title": "首页",
                "url": "/"
            },
        ]

        # print(request.breadcrumb)
        print(permission_list)

        for item in permission_list:
            reg = '^%s$' % item["url"]
            ret = re.search(reg, request.path)
            if ret:
                show_id = item["pid"] or item["id"]
                request.show_id = show_id  # 给request对象添加一个属性

                # 确定面包屑列表
                if item["pid"]:
                    ppermission = Permission.objects.filter(pk=item["pid"]).first()
                    request.breadcrumb.extend(
                        [{  # 父权限字典
                        "title": ppermission.title,
                        "url": ppermission.url
                        },
                        {  # 子权限字典
                            "title": item["title"],
                            "url": request.path
                        }]
                    )
                else:
                    request.breadcrumb.append(
                        {
                        "title": item["title"],
                        "url": item["url"]
                        }
                    )

                print("request.breadcrumb", request.breadcrumb)

                return None

        return HttpResponse('无权访问')