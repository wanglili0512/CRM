
import re
from django import template

register = template.Library()

@register.inclusion_tag("menu.html")
def get_menu_styles(request):
    permission_menu_dict = request.session.get("permission_menu_dict")

    for val in permission_menu_dict.values():
        val["class"] = ""
        for item in val["children"]:
            ret = re.search("^{}$".format(item["url"]), request.path)
            if ret:
                val["class"] = "active"

    return {"permission_menu_dict": permission_menu_dict}

@register.simple_tag
def get_role_url(request, rid):  # rid表示用户id
    params = request.GET.copy()
    params._mutable = True
    params['rid'] = rid
    return params.urlencode()