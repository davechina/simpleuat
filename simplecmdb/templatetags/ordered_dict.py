# -*-coding:utf-8 -*-
# Render dict into template in a specified order.

from django import template

# register
# 注册自定义标签和过滤器
register = template.Library()


# writting and registering custom template filters
@register.filter
def specified_key(value, arg):
    return value.get(arg)
