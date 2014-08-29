#-*-coding:utf-8 -*-
# Check if the img for pd is exists.

import os
import random
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

# register
register = template.Library()		# 注册自定义标签和过滤器


# writting and registering custom template filters
@register.filter
@stringfilter
def check_image(img):
	img_path = os.path.join(settings.STATIC_ROOT, 'color/img/5102/')
	all_img = map(lambda x : os.path.splitext(x)[0].lower().decode('gbk'), os.listdir(img_path))

	if img.lower() in all_img:
		return True


# writting and registering custom template filters
@register.simple_tag
def random_image(path):
	# img_path = os.path.join(settings.STATIC_ROOT, 'color/img/5102/')
	img_path = os.path.join(settings.STATIC_ROOT, path)
	rand_img = random.choice(os.listdir(img_path))
	print os.path.join(settings.STATIC_URL, path, u'%s' % rand_img)
	return os.path.join(settings.STATIC_URL, path, u'%s' % rand_img)
