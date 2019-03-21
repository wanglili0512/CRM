from django.urls import path, re_path

from app01 import views

urlpatterns = [
    # re_path('^$', views.index, name="index"),
    re_path(r'^reg/$', views.reg, name="reg"),

    re_path(r'^login/$', views.login, name="login"),
    re_path(r'^get_identifyCode/$', views.get_identifyCode, name="get_identifyCode"),

    re_path(r'^logout/$', views.logout, name="logout"),

    re_path(r'^index/$', views.index),

    # 1 客户管理
    re_path(r'^all_customers/$', views.CustomerView.as_view(), name="all_customers"),  # 所有客户列表
    re_path(r'^customers/list/$', views.CustomerView.as_view(), name="customers_list"),  # 公户列表
    re_path(r'^mycustomers/$', views.CustomerView.as_view(), name="mycustomers"),  # 我的客户列表
    re_path(r'^customer/add/$', views.AddEditCustomerView.as_view(), name="add_customer"),  # 添加客户
    re_path(r'^customer/edit/(\d+)$', views.AddEditCustomerView.as_view(), name="edit_customer"),  # 编辑客户

    re_path(r'^consult_records/$', views.ConsultRecordView.as_view(), name="consult_records"),  # 显示跟进记录列表
    re_path(r'^consult_records/add/$', views.AddEditConsultRecordView.as_view(), name="add_consult_record"),  # 添加跟进记录
    re_path(r'^consult_records/edit/(\d+)$', views.AddEditConsultRecordView.as_view(), name="edit_consult_record"),  # 编辑跟进记录

    re_path(r'^enrollments/$', views.EnrollmentView.as_view(), name="enrollments_list"),  # 显示报名记录列表
    re_path(r'^enrollments/add/$', views.AddEditEnrollmentView.as_view(), name="add_enrollments"),  # 添加报名记录
    re_path(r'^enrollments/edit/(\d+)$', views.AddEditEnrollmentView.as_view(), name="edit_enrollments"),  # 编辑报名记录

    # 3 统计管理
    path('tongji/', views.TongJiView.as_view(), name="tongji"), # 成单量统计

    # 4 班级管理
    path('classStudyRecord/', views.ClassStudyRecordView.as_view(), name="classStudyRecord"),  # 班级学习记录列表
    re_path(r'^classStudyRecord/add/$', views.AddEditCSRecordView.as_view(), name="add_csRecord"),  # 添加班级学习记录
    re_path(r'^classStudyRecord/edit/(\d+)$', views.AddEditCSRecordView.as_view(), name="edit_csRecord"),  # 编辑班级学习记录
    re_path(r'^classStudyRecord/del/(\d+)$', views.del_cs_record, name="del_csRecord"),  # 删除班级学习记录

    # 5 学生管理
    path('studentStudyRecord/', views.StudentStudyRecordView.as_view(), name="studentStudyRecord"),  # 学生学习记录列表
    re_path(r'^studentStudyRecord/add/$', views.AddEditSSRecordView.as_view(), name="add_ssRecord"),  # 添加学生学习记录
    re_path(r'^studentStudyRecord/edit/(\d+)$', views.AddEditSSRecordView.as_view(), name="edit_ssRecord"),  # 编辑学生学习记录
    re_path(r'^studentStudyRecord/del/(\d+)$', views.del_ss_record, name="del_ssRecord"),  # 删除班学生学习记录

    re_path(r'^student/inputscore/(\d+)$', views.InputScoreView.as_view(), name="inputscore"),   # 录入成绩

]