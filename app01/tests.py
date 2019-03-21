from django.test import TestCase

# Create your tests here.
import datetime

now1 = datetime.datetime.now()  # 年月日时分秒对象
now2 = datetime.datetime.today() # 年月日时分秒对象
today_date = datetime.datetime.now().date()  # 年月日对象
timenum = datetime.timedelta(days=1)  # 一天的时间差
yestoday = datetime.datetime.now().date() - timenum  # 今天 - 1 天 = 昨天
week = datetime.timedelta(weeks=1)  # 一周时间差


print(now1)  # 2018-11-24 21:53:37.290485
print(now2)  # 2018-11-24 21:53:37.290486
print(today_date)  # 2018-11-24
print(timenum)  # 1 day, 0:00:00
print(yestoday)  # 2018-11-23
print(week)  # 7 days, 0:00:00
