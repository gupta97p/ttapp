# -*- coding: utf-8 -*-
# @Author: Phu Hoang
# @Date:   2017-01-19 17:20:24
# @Last Modified by:   Phu Hoang
# @Last Modified time: 2017-01-19 18:57:18
from django import template


from django.contrib.contenttypes.models import ContentType

import re

from django.urls import reverse


class _Menu:
    parents = []
    children = []
    models_icon = {}

    def clear(self):
        self.parents = []
        self.children = []

    def add(self, label, link='', icon='', id_='', parent=''):

        if id_ == '':
            id_ = label

        if parent != '':
            child = {
                id_: {
                    'label': label,
                    'link': link,
                    'icon': icon,
                    'children': []
                }
            }

            self.children.append(child)

            for idx, parent_item in enumerate(self.parents):

                if parent in parent_item:
                    self.parents[idx][parent]['children'].append(child)
                else:
                    for idx, child_item in enumerate(self.children):
                        if parent in child_item:
                            self.children[idx][parent]['children'].append(child)

        else:
            self.parents.append({
                id_: {
                    'label': label,
                    'link': link,
                    'icon': icon,
                    'children': []
                }
            })

    def render(self, context, menus=None):
        menus = {} if menus is None else menus
        request = context['request']

        r = ''

        if len(menus) <= 0:
            # sorted(self.parents)
            menus = self.parents
            if(request.path == reverse('admin:index')):
                r = '<li class="active"><a href="' + reverse('admin:index') + '"><i class="fa fa-dashboard"></i> <span>Home</span></a></li>'
            else:
                r = '<li><a href="' + reverse('admin:index') + '"><i class="fa fa-dashboard"></i> <span>Home</span></a></li>'

        for group in menus:
            key = [key for key in group][0]
            icon = '<i class="fa fa-circle"></i>'

            if group[key]['icon'] != '':
                if re.match(r'\<([a-z]*)\b[^\>]*\>(.*?)\<\/\1\>', group[key]['icon']):
                    icon = group[key]['icon']
                else:
                    icon = '<i class="%s"></i>' % (group[key]['icon'])

            if len(group[key]['children']) > 0:
                r += '<li class="treeview"><a href="#">%s <span>%s</span><span class="pull-right-container"><i ' \
                     'class="fa fa-angle-left pull-right"></i></span></a><ul class="treeview-menu">\n' % (
                    icon, group[key]['label'])

                r += self.render(context, group[key]['children'])

                r += '</ul></li>\n'

            else:
                if(request.path == reverse('admin:index')):
                    r += '<li><a href="%s">%s <span>%s</span></a></li>\n' % (
                        group[key]['link'], icon, group[key]['label'])
                else:
                    r += '<li><a href="%s">%s <span>%s</span></a></li>\n' % (
                        group[key]['link'], icon, group[key]['label'])

        return r

    def admin_apps(self, context, r):
        request = context['request']
        for app in context['available_apps']:
            if app['name'] == 'Authentication and Authorization':
                continue
            for model in app['models']:
                model_name = model['object_name']
                model_instance = ContentType.objects.get(app_label=u'app', model=model_name).model_class()
                model_obj = model_instance.objects.filter()
                if 'add_url' in model:
                    url = model['add_url']
                if 'change_url' in model:
                    url = model['change_url']
                if 'admin_url' in model:
                    url = model['admin_url']
                icon = '<i class="fa fa-circle"></i>'
                object = model_obj.values()
                for j in object:
                    count = 0
                    c = ""
                    for k in object:
                        if j['id'] == k['parent_id']:
                            count += 1
                            child_name = k['name']
                            if model['object_name'].title() in self.models_icon:
                                if self.models_icon[model['object_name'].title()] != '':
                                    if re.match(r'\<([a-z]*)\b[^\>]*\>(.*?)\<\/\1\>',
                                                self.models_icon[model['object_name'].title()]):
                                        icon = self.models_icon[model['object_name'].title()]
                                    else:
                                        icon = '<i class="%s"></i>' % (self.models_icon[model['object_name'].title()])
                            if request.path == url:
                                c += '<li><a href="%s">%s %s</a></li>' % (url, icon, child_name)
                            else:
                                c += '<li><a href="%s">%s %s</a></li>' % (url, icon, child_name)
                    if count > 0:
                        r += '<li class="treeview"><a href="#"><i class="fa fa-circle"></i><span>%s</span>' \
                             '<span class="pull-right-container"><i class="fa fa-angle-left pull-right"></i></span>' \
                             '</a><ul class="treeview-menu">' % j['name'] + c
                    elif j['name'] not in r:
                        if request.path == url:
                            r += '<li><a href="%s">%s %s</a></li>' % (url, icon, j['name'])
                        else:
                            r += '<li><a href="%s">%s %s</a></li>' % (url, icon, j['name'])
                    if c != "":
                        r += '</ul>'
                    c, count = "", 0
        return r

    def set_model_icon(self, model_name, icon):
        self.models_icon[model_name.title()] = icon

    def get_model_icon(self, context):

        icon = '<i class="fa fa-circle-o"></i>'
        if context['model']['object_name'].title() in self.models_icon:

            if self.models_icon[context['model']['object_name'].title()] != '':
                if re.match(r'<([a-z]*)\b[^>]*>(.*?)</\1>', self.models_icon[context['model']['object_name'].title()]):
                    icon = self.models_icon[context['model']['object_name']]
                else:
                    icon = '<i class="%s"></i>' % (self.models_icon[context['model']['object_name'].title()])

        return icon


register = template.Library()

Menu = _Menu()


@register.simple_tag(takes_context=True, name='menu')
def menu_tag(context):
    return Menu.admin_apps(context, Menu.render(context))


@register.simple_tag(takes_context=True, name='icon')
def icon_tag(context):
    return Menu.get_model_icon(context)
