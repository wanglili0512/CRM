from rbac.models import Role

def initial_session(user_obj, request):
    """
    将当前登录人的所有权限url列表和
    自己构建的所有菜单权限字典和
    权限表name字段列表注入session
    :param user_obj: 当前登录用户对象
    :param request:  请求对象HttpRequest
    """
    # 查询当前登录人的所有权限列表
    ret = Role.objects.filter(user=user_obj).values('permissions__url',
                                                    'permissions__title',
                                                    'permissions__name',
                                                    'permissions__pk',
                                                    'permissions__pid',
                                                    'permissions__menu__title',
                                                    'permissions__menu__icon',
                                                    'permissions__menu__id').distinct()
    permission_list = []
    permission_names = []
    permission_menu_dict = {}
    for item in ret:
        # 获取用户权限列表用于中间件中权限校验，改变数据结构
        permission_list.append({
            'url':item['permissions__url'],
            'id':item['permissions__pk'],
            'pid':item['permissions__pid'],
            'title':item['permissions__title']
        })
        # 获取权限表name字段用于动态显示权限按钮
        permission_names.append(item['permissions__name'])

        menu_pk = item['permissions__menu__id']
        if menu_pk:
            if menu_pk not in permission_menu_dict:
                permission_menu_dict[menu_pk] = {
                    "menu_title": item["permissions__menu__title"],
                    "menu_icon": item["permissions__menu__icon"],
                    "children": [
                        {
                            "title": item["permissions__title"],
                            "url": item["permissions__url"],
                 "pk": item["permissions__pk"]
                        }
                    ],
                }
            else:
                permission_menu_dict[menu_pk]["children"].append({
                    "title": item["permissions__title"],
                    "url": item["permissions__url"],
                })
    print('权限列表', permission_list)
    print('权限表中url的别名字段', permission_names)
    print('菜单权限', permission_menu_dict)

    # 将当前登录人的权限列表注入session中
    request.session['permission_list'] = permission_list

    # 将权限表name字段列表注入session中
    request.session['permission_names'] = permission_names

    # 将当前登录人的菜单权限字典注入session中
    request.session['permission_menu_dict'] = permission_menu_dict