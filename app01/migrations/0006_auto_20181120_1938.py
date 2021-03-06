# Generated by Django 2.1.3 on 2018-11-20 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_auto_20181119_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='部门名称')),
                ('count', models.IntegerField(verbose_name='人数')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='deal_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='classstudyrecord',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='讲师'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='depart',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app01.Department', verbose_name='所属部门'),
        ),
    ]
