# -*- coding: utf8 -*-


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
import xdrlib, sys, xlrd, datetime

from models import *

def hello(request):
    return HttpResponse("Hello world")

@csrf_protect
def login(request):
	if request.method == 'GET':
		return show_login_view(request, False)
		# return render_to_response('/static/login.html')
	elif request.method == 'POST':
		username = request.POST.get('user', '')
		password = request.POST.get('password', '')
		user     = auth.authenticate(username=username, password=password)
		print "user: %s, password: %s" % (username, password)
		if user is not None and user.is_active:
			# Correct password, and the user is marked "active"
			auth.login(request, user)
			# Redirect to a success page.
			return HttpResponseRedirect("/main/")
		else:
			return show_login_view(request, True)

		# if ('user' in request.POST and request.POST['user']) and \
		# 	('password' in request.POST and request.POST['password']):
		# 	user = User.objects.filter(user = request.POST['user'], password = request.POST['password'])
		# 	if user:
		# 		return HttpResponseRedirect('/main')
		# else:
		# 	print "error"
		# 	t    = get_template('login.html')
		# 	html = t.render(RequestContext(request, {'error': True}))
		# 	return HttpResponse(html)


def main(request):
	if request.user.is_authenticated():
		t      = get_template('index.html')
		action = request.GET.get('action', '')
		print "action: %s" % (action)
		if action == '':
			return show_default_main_view(request, t)
		elif action == 'msg':
			return show_msg_view(request, t)
		elif action == 'req_valid':
			return show_req_valid_view(request, t)
		elif action == 'check_onu_valid':
			return show_check_valid_view(request, t)
		elif action == 'check_eoc_valid':
			return show_check_valid_view(request, t)
		elif action == 'query':
			return show_query_view(request, t)
	else:
		return show_login_view(request, True)


# ============================help function=====================================
def show_login_view(request, is_error):
	t    = get_template('login.html')
	html = t.render(RequestContext(request, {'error': is_error}))
	return HttpResponse(html)

def show_default_main_view(request, t_html):
	action = request.GET.get('action', '')
	dic = {'user': request.user.username, 
		   'action': action,
		   'msg_len': get_message_len(request.user.username)
		  }
	return HttpResponse(t_html.render(RequestContext(request, dic)))
	

def show_msg_view(request, t_html):
	action  = request.GET.get('action', '')
	my_msgs = Message.objects.filter(user = request.user.username).order_by('-report_date')
	dic = {'user': request.user.username, 
		   'action': action,
		   'msg_list': my_msgs,
		   'msg_len': get_message_len(request.user.username)
		  }
	return HttpResponse(t_html.render(Context(dic)))


def get_message_len(username):
	return len(Message.objects.filter(user = username))


def show_req_valid_view(request, t_html):
	action = request.GET.get('action', '')
	dic = {'user': request.user.username, 
		   'action': action,
		   'msg_len': get_message_len(request.user.username),
		   'valider_list': User.objects.all()
		  }
	return HttpResponse(t_html.render(RequestContext(request, dic)))

def show_check_valid_view(request, t_html):
	action   = request.GET.get('action', '')
	username = request.user.username
	dic = {'user': username, 
		   'action': action,
		   'msg_len': get_message_len(username)
		  }
	if action == 'check_onu_valid':
		dic['onu_check_list'] = get_onu_detail_report(username)
	elif action == 'check_eoc_valid':
		dic['eoc_check_list'] = get_eoc_detail_report(username)
	return HttpResponse(t_html.render(RequestContext(request, dic)))


def get_onu_detail_report(username):
	return ONUDetailReport.objects.raw(
		('select install_valid_devonu_tmp.dev_id, user, date, addr_1, addr_2, addr_detail, dev_name, mac_addr, port_remark '
				'from install_valid_devonu_tmp, install_valid_devreport '
				'where to_who=\'%s\' and dev_type=1 and is_valid=0 '
				'and install_valid_devonu_tmp.dev_id=install_valid_devreport.dev_id '
				'order by date') % (username))

def get_eoc_detail_report(username):
	return EOCDetailReport.objects.raw(
		('select install_valid_deveoc_tmp.dev_id, user, date, addr_1, addr_2, addr_detail, '
		 'line_box_type, dev_box_type, install_valid_deveoc_tmp.dev_type, cover_users, '
		 'model, manager_ip, ip_mask, gateway, manager_vlan, port_begin_valn, port_end_valn '
				'from install_valid_deveoc_tmp, install_valid_devreport '
				'where to_who=\'%s\' and install_valid_devreport.dev_type=2 and is_valid=0 '
				'and install_valid_deveoc_tmp.dev_id=install_valid_devreport.dev_id '
				'order by date') % (username))

@csrf_protect
def upload(request):
	if request.method == 'POST' and request.FILES['file'] is not None:
		print "ok, upload: %s" % (request.FILES['file'])
		handle_upload(request.FILES['file'], request)
	t = get_template('upload_succ.html')
	return HttpResponse(t.render(RequestContext(request, {})))


def handle_upload(f, request):
	# to-do: temp文件要唯一
	tmp_file = ('%s_tmp.xlsx') % (request.user.username)
	print tmp_file
	destination = open(tmp_file, 'wb+')
	for chunk in f.chunks():
		destination.write(chunk)
	destination.close()

	xml_data = xlrd.open_workbook(tmp_file)
	upload_onu_dev(request, xml_data)
	upload_eoc_dev(request, xml_data)


def upload_onu_dev(request, xml_data):
	table = xml_data.sheet_by_name(u'onu')
	# 循环行列表数据
	for i in range(1, table.nrows):
		# 保存等待验收的设备临时数据
		dev_id = len(DevONU_TMP.objects.all()) + 1
		dev = DevONU_TMP(dev_id      = dev_id,
						 addr_1      = table.cell(i, 0).value,
						 addr_2      = table.cell(i, 1).value,
						 addr_detail = table.cell(i, 2).value,
						 dev_name    = table.cell(i, 3).value,
						 mac_addr    = table.cell(i, 4).value,
						 port_remark = table.cell(i, 5).value)
		dev.save()
		# 然后保存提交记录
		date     = datetime.datetime.now()
		dev_type = 1
		report = DevReport(	user     = request.user.username, 
							to_who   = request.POST.get('valider', ''),
							dev_id   = dev_id,
							dev_type = dev_type,
							date     = date,
							is_valid = False)
		report.save()
		# 再向验证者发送消息
		msg_id = len(Message.objects.all()) + 1
		msg = Message(msg_id      = msg_id,
					  user        = request.POST.get('valider', ''),
					  msg_type    = 1,
					  from_who    = request.user.username,
					  dev_type    = dev_type,
					  report_date = date,
					  is_read     = False)
		msg.save()

def upload_eoc_dev(request, xml_data):
	table = xml_data.sheet_by_name(u'eoc')
	# 循环行列表数据
	for i in range(1, table.nrows):
		# 保存等待验收的设备临时数据
		dev_id = len(DevEOC_TMP.objects.all()) + 1
		dev = DevEOC_TMP(dev_id          = dev_id,
						 addr_1          = table.cell(i, 0).value,
						 addr_2          = table.cell(i, 1).value,
						 addr_detail     = table.cell(i, 2).value,
						 line_box_type   = table.cell(i, 3),
						 dev_box_type    = table.cell(i, 4),
						 dev_type        = table.cell(i, 5),
						 cover_users     = table.cell(i, 6),
						 model           = table.cell(i, 7),
						 manager_ip      = table.cell(i, 8),
						 ip_mask         = table.cell(i, 9),
						 gateway         = table.cell(i, 10),
						 manager_vlan    = table.cell(i, 11),
						 port_begin_valn = table.cell(i, 12),
						 port_end_valn   = table.cell(i, 13))
		dev.save()
		# 然后保存提交记录
		date     = datetime.datetime.now()
		dev_type = 2
		report = DevReport(	user     = request.user.username, 
							to_who   = request.POST.get('valider', ''),
							dev_id   = dev_id,
							dev_type = dev_type,
							date     = date,
							is_valid = False)
		report.save()
		# 再向验证者发送消息
		msg_id = len(Message.objects.all()) + 1
		msg = Message(msg_id      = msg_id,
					  user        = request.POST.get('valider', ''),
					  msg_type    = 1,
					  from_who    = request.user.username,
					  dev_type    = dev_type,
					  report_date = date,
					  is_read     = False)
		msg.save()

def valid_dev(request):
	print request.POST.get('_selected_action')
	int(request)
