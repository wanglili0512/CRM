from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import random

from django.http.request import QueryDict   # 读源码用
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.views import View

from app01.form import UserInfoModelForm, CustomerModelForm, ConsultRecordModelForm, EnrollmentModelForm
from app01.utils.page import Pagination
from app01.models import UserInfo, Customer, ConsultRecord, Enrollment

# 注册
def reg(request):
    if request.method == "POST":
        print("request.POST", type(request.POST), request.POST)
        form = UserInfoModelForm(request.POST)
        res = {"user": None, "err_msg": ""}
        if form.is_valid():
            res["user"] = form.cleaned_data.get("username")
            print("cleaned_data", form.cleaned_data)
            del form.cleaned_data["r_pwd"]   # 删除确认密码字段，因为表中无此字段，只需要校验，不用插入
            UserInfo.objects.create_user(**form.cleaned_data)
            # form.save()  # ？？？此句翻译成了create，因此密码是明文显示，如何翻译成create_user，即密码加密
        else:
            print("form.errors", form.errors)
            print("form.cleaned_data", form.cleaned_data)
            res["err_msg"] =form.errors
        return JsonResponse(res)
    else:   # get请求
        print("request.POST", type(request.POST), request.POST)
        form = UserInfoModelForm()
        return  render(request, "reg.html", {"form": form})



# 登录
from rbac.models import User
from rbac.service.setsession import initial_session
def login(request):
    if request.is_ajax():
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        validcode = request.POST.get('validcode')

        response = {"user": None, "err_msg": ""}
        if validcode.upper() == request.session.get("keep_str").upper():      # 验证码正确
            user_obj = User.objects.filter(name=user, password=pwd).first()   # 根据用户输入去rbac的User表查询中
            if user_obj:   # 用户存在,验证通过
                response["user"] = user
                request.session['user_id'] = user_obj.pk   # 用户id注入session，用来保存用户信息，表示用户已经登录
                # 将权限列表和权限菜单列表注入session
                initial_session(user_obj, request)
            else:          # 用户验证不通过
                response['err_msg'] = "用户名或者密码错误！"
            return JsonResponse(response)
    # get请求
    return render(request, 'login.html')


# 随机生成验证码图片
def get_identifyCode(request):

    def get_random_color():
        return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def get_random_char():
        random_num = str(random.randint(0, 9))
        random_lower = chr(random.randint(97, 122))
        random_upper = chr(random.randint(65, 90))
        return random.choice([random_num, random_lower, random_upper])

    img = Image.new("RGB", (88, 30), (255,255,255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("static/font/kumo.ttf", 32)

    keep_str = ""
    for i in range(4):
        random_char = get_random_char()
        draw.text((i*88/4, 0), random_char, get_random_color(), font=font)
        keep_str += random_char

    # 写干扰点
    for i in range(40):
        draw.point([random.randint(0, 88), random.randint(0, 30)], fill=get_random_color())
    # 写干扰圆圈
    for i in range(10):
        draw.point([random.randint(0, 88), random.randint(0, 30)], fill=get_random_color())
        x = random.randint(0, 88)
        y = random.randint(0, 30)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())
    # 画干扰线
    for i in range(5):
        x1 = random.randint(0, 88)
        y1 = random.randint(0, 30)
        x2 = random.randint(0, 88)
        y2 = random.randint(0, 30)
        draw.line((x1, y1, x2, y2), fill=get_random_color())
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    # 写与读（内存中）
    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()

    print('keep_str', keep_str)
    # 将验证码存在各自的session中（一定不能设为全局变量）
    request.session['keep_str'] = keep_str

    return HttpResponse(data)


# 注销
def logout(request):
    del request.session["user_id"]
    return redirect("/login/")


# index
def index(request):
    return render(request, "index.html")


# 查看客户列表
class CustomerView(View):
    def get(self, request):  # get请求
        if reverse("all_customers") == request.path:
            head_text = "所有客户"
            customer_list = Customer.objects.all()
        elif reverse("customers_list") == request.path:
            head_text = "公户列表"
            customer_list = Customer.objects.filter(consultant__isnull=True)  # 注意：判断一个字段是不是为空，一定不能写consultant=""
        else:
            head_text = "我的客户"
            user_id = request.session["user_id"]
            userinfo_obj = UserInfo.objects.filter(user_rbac_id=user_id).first()
            customer_list = Customer.objects.filter(consultant=userinfo_obj)

        # search过滤
        field = request.GET.get('field')       # 搜索字段
        val = request.GET.get("q")             # 搜索关键字
        if val:
            q = Q()   # Q实例化，Q继承了tree.Node类，Node类有children属性，是一个列表，append条件
            q.children.append((field + "__contains", val))   # q.children.append(('name_contains', 'wang'))
            customer_list = customer_list.filter(q)          # 按照上面的条件过滤(name__contains=wang)

        # 分页
        current_page_num = request.GET.get("page")      # 取出用户发送的"页码数"
        pagination = Pagination(current_page_num, customer_list.count(), request)    # 调用分页器组件
        customer_list = customer_list[pagination.start:pagination.end]

        path = request.path        # 当前请求路径
        next = "?next=%s" % path   # 封装当前请求路径为url中的参数，与next组成键值对，传到页面
        # 因为公户列表，所有客户，我的客户中都有添加客户的按钮，添加成功后要自动跳转到进入之前的页面，所以加next参数来标识

        return render(request, "customer/customer_list.html", {"next": next, "head_text": head_text, "customer_list": customer_list, "pagination": pagination})

    def post(self, request):   # post请求
        # action的批量处理
        print(request.POST)
        func_str = request.POST.get("action")
        data = request.POST.getlist("selected_pk_list")
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            func = getattr(self, func_str)
            queryset = Customer.objects.filter(pk__in=data)
            res = func(request,queryset)
            if res:
                return res    # 批量公户转私户手速慢的时候执行
            ret = self.get(request)    # 注意：这里自动执行一边get方法，不用再重定向一次了
            return ret

    def patch_delete(self, request, queryset):   # 批量删除
        queryset.delete()

    def patch_reverse_s(self, request, queryset):  # 批量公户转私户
        result = queryset.filter(consultant__isnull=True)
        if result:
            result.update(consultant=request.user)
        else:
            return HttpResponse("你手太慢了！")

    def patch_reverse_g(self, request, queryset):  # 批量私户转公户
        queryset.update(consultant=None)


# 添加客户:未整合
class AddCustomerView2(View):
    def get(self,request):
        form = CustomerModelForm()
        return render(request,"add_edit_consultrecord.html",{"form": form })

    def post(self,request):
        form=CustomerModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('customers_list'))
        else:
            return render(request,"add_edit_consultrecord.html", {"form":form})
# 编辑客户:未整合
class EditCustomerView2(View):
    def get(self,request,id):
        edit_obj = Customer.objects.get(pk=id)    # 注意：此处是get方法获取到model对象，这里不能是queryset类型，用filter过滤要加索引取出model对象
        form = CustomerModelForm(instance=edit_obj)
        return render(request,"add_edit_customer.html",{"form": form })

    def post(self,request,id):
        edit_obj = Customer.objects.get(pk=id)
        form=CustomerModelForm(request.POST,instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(request.GET.get("next"))
        else:
            return render(request,"add_edit_customer.html", {"form":form})


# 编辑/添加客户:整合后
class AddEditCustomerView(View):
    # 得到添加页面和编辑页面，注意：之所以给一个默认值参数，因为添加时不需要参数，编辑时需要传递编辑的记录id
    def get(self, request, edit_id=None):
        # 当edit_id=None时，Customer.objects.filter(pk=edit_id).first() 为空
        edit_obj = Customer.objects.filter(pk=edit_id).first()    # 注意：这里不能是queryset类型，用filter过滤要加first()方法取出model对象
        form = CustomerModelForm(instance=edit_obj)   # 添加时表单内容为空，编辑时页面显示数据库拿到的内容，因为instance一个为空对象，一个为model对象
        return render(request, "customer/add_edit_customer.html", {"form": form, "edit_obj": edit_obj})
        # form是CustomerModelForm类实例化对象，传到页面渲染表单，edit_obj是否有值决定页面显示编辑（有值）还是添加（空）


    # 提交添加页面和编辑页面
    def post(self, request, edit_id=None):
        # 编辑时查询出编辑对象，提交时也执行查询，但查询结果为空
        edit_obj = Customer.objects.filter(pk=edit_id).first()

        # request.POST是用户提交的数据，instance有值则执行update操作，为空则执行create操作
        form=CustomerModelForm(request.POST,instance=edit_obj)

        if form.is_valid():    # 校验用户的数据合法
            form.save()     # 取决于form对象实例化时instance参数是否有值，有值则update，为空则create操作
            # 下面重定向的url需要从请求对象中获取，因为请求携带的参数中标识用户是从哪个url跳转过来的，更新或者创建完之后重新跳转回那个url
            # 因为所有客户，我的客户，公户列表都有进入这个url（添加客户）的入口
            return redirect(request.GET.get("next"))
        else:
            return render(request, "customer/add_edit_customer.html", {"form": form, "edit_obj": edit_obj})


# 显示跟进记录列表
class ConsultRecordView(View):
    def get(self, request):

        user_id = request.session["user_id"]   # 拿到当前登录人id，即rbac用户表中的用户id
        userinfo_obj = UserInfo.objects.filter(user_rbac_id=user_id).first()  # 根据rbac的用户查询出app01的用户对象
        consult_record_list = ConsultRecord.objects.filter(consultant=userinfo_obj)  # 根据app01中的用户对象查询对应销售是该用户的跟进记录

        # 当用户url中含有参数customer_id=2的时候，说明是从用户列表中点击跟进详情链接进入的，则从上面该销售人的跟进记录中进一步筛选跟进记录
        customer_id = request.GET.get("customer_id")
        if customer_id:
            consult_record_list = consult_record_list.filter(customer_id=customer_id)

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, consult_record_list.count(), request)
        consult_record_list = consult_record_list[pagination.start:pagination.end]

        return render(request, "customer/consultrecord.html", {"consult_record_list":consult_record_list, "pagination":pagination})


# 编辑/添加跟进记录
class AddEditConsultRecordView(View):
    def get(self, request, edit_id=None):
        edit_obj = ConsultRecord.objects.filter(pk=edit_id).first()    # 注意：这里不能是queryset类型，用filter过滤要加first()方法取出model对象
        form = ConsultRecordModelForm(instance=edit_obj)
        return render(request, "customer/add_edit_consultrecord.html", {"form": form, "edit_obj": edit_obj})

    def post(self, request, edit_id=None):
        edit_obj = ConsultRecord.objects.filter(pk=edit_id).first()
        form=ConsultRecordModelForm(request.POST,instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('consult_records'))  # 因为添加跟进记录只在跟进记录列表进入，因此只需要反向解析，不需要判断从哪个页面进来
        else:
            return render(request, "customer/add_edit_consultrecord.html", {"form": form, "edit_obj": edit_obj})


# 显示报名记录列表
class EnrollmentView(View):
    def get(self, request):
        enrollment_list = Enrollment.objects.all()

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, enrollment_list.count(), request)
        enrollment_list = enrollment_list[pagination.start:pagination.end]

        return render(request, "customer/enrollment_list.html", {"enrollment_list": enrollment_list, "pagination": pagination})


# 编辑/添加报名记录
class AddEditEnrollmentView(View):
    def get(self, request, edit_id=None):
        edit_obj = Enrollment.objects.filter(pk=edit_id).first()    # 注意：这里不能是queryset类型，用filter过滤要加first()方法取出model对象
        form = EnrollmentModelForm(instance=edit_obj)
        return render(request, "customer/add_edit_enrollment.html", {"form": form, "edit_obj": edit_obj})

    def post(self, request, edit_id=None):
        edit_obj = Enrollment.objects.filter(pk=edit_id).first()
        form = EnrollmentModelForm(request.POST,instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('enrollments_list'))
        else:
            return render(request, "customer/add_edit_enrollment.html", {"form": form, "edit_obj": edit_obj})



# ################################ 学员管理 ##########################################
from app01.models import ClassStudyRecord, StudentStudyRecord, Student
from app01.form import CSRecordModelForm, SSRecordModelForm, InputSSRecordModelForm
# 班级学习记录
class ClassStudyRecordView(View):
    def get(self, request):
        cs_record_list = ClassStudyRecord.objects.all()

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, cs_record_list.count(), request)
        cs_record_list = cs_record_list[pagination.start:pagination.end]

        return render(request, 'student/cs_record_list.html', {"cs_record_list": cs_record_list, "pagination": pagination})


    def post(self, request):   # post请求
        # action的批量处理
        print(request.POST)
        func_str = request.POST.get("action")
        data = request.POST.getlist("selected_pk_list")
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            func = getattr(self, func_str)
            queryset = ClassStudyRecord.objects.filter(pk__in=data)
            func(request,queryset)

            ret = self.get(request)    # 注意：这里自动执行一次get方法，不用再重定向一次了
            return ret

    def patch_delete(self, request, queryset):   # 批量删除班级学习记录
        queryset.delete()

    def patch_create(self, request, queryset):   # 批量创建学生学习记录
        try:  # 限制一个班级只能初始化一次
            for cs_record_obj in queryset:
                student_list = cs_record_obj.class_obj.student_set.all()
                for stu_obj in student_list:
                    StudentStudyRecord.objects.create(
                        student = stu_obj,
                        classstudyrecord = cs_record_obj
                    )
        except Exception as e:
            pass


# 编辑/添加班级学习记录
class AddEditCSRecordView(View):
    def get(self, request, edit_id=None):
        edit_obj = ClassStudyRecord.objects.filter(pk=edit_id).first()    # 注意：这里不能是queryset类型，用filter过滤要加first()方法取出model对象
        form = CSRecordModelForm(instance=edit_obj)
        return render(request, "student/add_edit_CSR.html", {"form": form, "edit_obj": edit_obj})

    def post(self, request, edit_id=None):
        edit_obj = ClassStudyRecord.objects.filter(pk=edit_id).first()
        form = CSRecordModelForm(request.POST,instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('classStudyRecord'))
        else:
            return render(request, "student/add_edit_CSR.html", {"form": form, "edit_obj": edit_obj})


# 删除班级学习记录
def del_cs_record(request, del_id):
    ClassStudyRecord.objects.filter(pk=del_id).delete()
    return redirect(reverse('classStudyRecord'))


# 查看学生学习记录
class StudentStudyRecordView(View):
    def get(self, request):
        ss_record_list = StudentStudyRecord.objects.all()

        # 分页
        current_page_num = request.GET.get("page")
        pagination = Pagination(current_page_num, ss_record_list.count(), request)
        ss_record_list = ss_record_list[pagination.start:pagination.end]

        return render(request, 'student/ss_record_list.html', {"ss_record_list": ss_record_list, "pagination": pagination})


    def post(self, request):   # post请求
        # action的批量处理
        print(request.POST)
        func_str = request.POST.get("action")
        data = request.POST.getlist("selected_pk_list")
        if not hasattr(self, func_str):
            return HttpResponse("非法输入")
        else:
            func = getattr(self, func_str)
            queryset = StudentStudyRecord.objects.filter(pk__in=data)
            func(request, queryset)

            ret = self.get(request)    # 注意：这里自动执行一边get方法，不用再重定向一次了
            return ret

    def patch_delete(self, request, queryset):   # 批量删除学生学习记录
        queryset.delete()


# 编辑/添加学生学习记录
class AddEditSSRecordView(View):
    def get(self, request, edit_id=None):
        edit_obj = StudentStudyRecord.objects.filter(pk=edit_id).first()    # 注意：这里不能是queryset类型，用filter过滤要加first()方法取出model对象
        form = SSRecordModelForm(instance=edit_obj)
        return render(request, "student/add_edit_SSR.html", {"form": form, "edit_obj": edit_obj})

    def post(self, request, edit_id=None):
        edit_obj = StudentStudyRecord.objects.filter(pk=edit_id).first()
        form = SSRecordModelForm(request.POST,instance=edit_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('studentStudyRecord'))
        else:
            return render(request, "student/add_edit_SSR.html", {"form": form, "edit_obj": edit_obj})


# 删除学生学习记录(按钮单个删除)
def del_ss_record(request, del_id):
    StudentStudyRecord.objects.filter(pk=del_id).delete()
    return redirect(reverse('studentStudyRecord'))


# 录入成绩：基于modelformset组件
from django.forms.models import modelformset_factory
class InputScoreView(View):
    def get(self, request, csRecord_id):
        model_formset_cls = modelformset_factory(model=StudentStudyRecord, form=InputSSRecordModelForm, extra=0)
        queryset = StudentStudyRecord.objects.filter(classstudyrecord=csRecord_id)
        formset = model_formset_cls(queryset=queryset)
        return render(request, 'student/stu_score_list.html', {'formset': formset})

    def post(self, request, csRecord_id):
        model_fromset_cls = modelformset_factory(model=StudentStudyRecord, form=InputSSRecordModelForm, extra=0)
        formset = model_fromset_cls(request.POST)
        if formset.is_valid():
            formset.save()
        return self.get(request, csRecord_id)


# 成单量统计:未整合
import datetime
from django.db.models import Count
class TongJiView2(View):
    def today(self):  # 今天
        today = datetime.datetime.now().date()
        customer_list = Customer.objects.filter(deal_date=today)
        # 查询每个销售的名字以及对应的销售今天的成单量
        ret = UserInfo.objects.filter(depart_id=2, customers__deal_date=today).annotate(c=Count("customers")).values_list("username", "c")
        ret = [[item[0], item[1]] for item in list(ret)]
        return {'customer_list': customer_list, 'ret': ret}

    def yesterday(self):  # 昨天
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        customer_list = Customer.objects.filter(deal_date=yesterday)
        # 查询每个销售的名字以及对应的销售昨天的成单量
        ret = UserInfo.objects.filter(depart_id=2, customers__deal_date=yesterday).annotate(c=Count("customers")).values_list("username", "c")
        ret = [[item[0], item[1]] for item in list(ret)]
        return {'customer_list': customer_list, 'ret': ret}

    def week(self):  # 最近一周
        today = datetime.datetime.now().date()
        weekago = datetime.datetime.now().date() - datetime.timedelta(weeks=1)
        customer_list = Customer.objects.filter(deal_date__gte=weekago, deal_date__lte=today)
        # 查询每个销售的名字以及对应的销售最近一周内的成单量
        ret = UserInfo.objects.filter(depart_id=2, customers__deal_date__gte=weekago, customers__deal_date__lte=today).annotate(c=Count("customers")).values_list("username", "c")
        ret = [[item[0], item[1]] for item in list(ret)]
        return {"customer_list": customer_list, "ret": ret}

    def recent_month(self):  # 最近一个月
        today = datetime.datetime.now().date()
        monthago = datetime.datetime.now().date() - datetime.timedelta(days=30)
        customer_list = Customer.objects.filter(deal_date__gte=monthago, deal_date__lte=today)
        # 查询每个销售的名字以及对应的销售最近一个月内的成单量
        ret = UserInfo.objects.filter(depart_id=2, customers__deal_date__gte=monthago, customers__deal_date__lte=today).annotate(c=Count("customers")).values_list("username", "c")
        ret = [[item[0], item[1]] for item in list(ret)]
        return {"customer_list": customer_list, "ret": ret}

    def get(self, request):
        date = request.GET.get("date", "today")
        if hasattr(self, date):
            context = getattr(self, date)()
        return render(request, 'customer/tongji.html', context)


# 成单量统计：整合后
class TongJiView(View):
    def get(self,request):
        date = request.GET.get("date", "today")
        now = datetime.datetime.now().date()
        delta1 = datetime.timedelta(days=1)
        delta2 = datetime.timedelta(weeks=1)
        delta3 = datetime.timedelta(days=30)
        condition = {
            "today":[{"deal_date":now},{"customers__deal_date":now}],
            "yesterday":[{"deal_date":now - delta1},{"customers__deal_date":now - delta1}],
            "week":[
                {"deal_date__gte":now-delta2, "deal_date__lte":now},
                {"customers__deal_date__gte":now-delta2, "customers__deal_date__lte":now}
                ],
            "recent_month":[
                {"deal_date__gte":now - delta3, "deal_date__lte":now},
                {"customers__deal_date__gte":now - delta3, "customers__deal_date__lte":now}
                ],
              }
        customer_list = Customer.objects.filter(**(condition.get(date)[0]))
        ret = UserInfo.objects.all().filter(**(condition.get(date)[1])).annotate(c=Count("customers")).values_list("username","c")
        ret_x = [item[0] for item in list(ret)]
        ret_y = [item[1] for item in list(ret)]
        return render(request,"customer/tongji.html", {'customer_list': customer_list, 'ret_x': ret_x, 'ret_y': ret_y})

