# Generated by Django 2.1.3 on 2018-11-21 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0001_initial'),
        ('app01', '0007_auto_20181121_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='user_rbac',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.User', verbose_name='rbac用户'),
        ),
    ]
