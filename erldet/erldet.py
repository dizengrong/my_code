from fabric.api import local
from fabric import operations as fabric_op
from fabric.api import env, run, cd
from xml.dom import minidom
from os import path

# hosts parsed from deploy configure file: deploy_cfg.xml
g_hosts = None
# app name is the folder name under deploy_path,
# which used to check if already deployed
g_app_data = None
# if need to run task on single host, set this value
g_single_host = None

def get_attrvalue(node, attrname):
	return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
	return node.childNodes[index].nodeValue if node else ''

def get_xmlnode(node, name):
	return node.getElementsByTagName(name) if node else []

def get_hosts_and_app(file_name):
	doc         = minidom.parse(file_name)
	root        = doc.documentElement
	
	app_name    = get_nodevalue(get_xmlnode(root, 'name')[0])
	app_archive = get_nodevalue(get_xmlnode(root, 'archive')[0])
	app_data    = {'name':app_name, 'archive':app_archive}
	
	host_nodes  = get_xmlnode(get_xmlnode(root, 'hosts')[0], 'host')
	host_dict   = {}
	for node in host_nodes:
		app_id        = get_nodevalue(get_xmlnode(node, 'app_id')[0])
		host_name     = get_nodevalue(get_xmlnode(node, 'name')[0])
		password      = get_nodevalue(get_xmlnode(node, 'password')[0])
		deploy_path   = get_nodevalue(get_xmlnode(node, 'deploy_path')[0])
		run_script    = get_nodevalue(get_xmlnode(node, 'run_script')[0])
		stop_script   = get_nodevalue(get_xmlnode(node, 'stop_script')[0])
		status_script = get_nodevalue(get_xmlnode(node, 'status_script')[0])
		datas_nodes = get_xmlnode(node, 'datas_config')
		if datas_nodes != []:
			datas_node     = datas_nodes[0]
			svn_path       = get_nodevalue(get_xmlnode(datas_nodes, 'svn_path')[0])
			datas_desc_xml = get_nodevalue(get_xmlnode(datas_nodes, 'datas_desc_xml')[0])
			save_path      = get_nodevalue(get_xmlnode(datas_nodes, 'save_path')[0])
			
			datas_config   = (svn_path, datas_desc_xml, save_path)
		else:
			datas_config = None

		
		host_data   = {'name': host_name, 
					   'app_id': app_id,
					   'password': password,
					   'deploy_path': deploy_path,
					   'run_script': run_script,
					   'stop_script': stop_script,
					   'status_script': status_script,
					   'datas_config': datas_config}
		host_dict[app_id] = host_data

	return (app_data, host_dict)


def set_hosts():
	(app_data, host_dict) = get_hosts_and_app('deploy_cfg.xml')
	env.hosts             = host_dict
	g_app_data            = app_data

# @hosts(g_single_host)
def deploy(host_data):
	if not is_deploy(host_data, g_app_data['name']):
		env.host_string = 'root@' + host_data['name']
		env.password = host_data['password']
		basename = path.basename(full_path),
		fabric_op.put(g_app_data['archive'], host_data['deploy_path'])
		with fabric_op.cd(host_data['deploy_path']):
			run('tar xzf ' + basename)
	else:
		print("already deployed, host data: %s" % host_data)

def deploy_all():
	for host_data in env.hosts:
		deploy(host_data)

def is_deploy(host_data, app_name):
	False # TO-DO: check if the path exist

def start(host_data):
	env.host_string = 'root@' + host_data['name']
	env.password = host_data['password']
	with fabric_op.cd(host_data['deploy_path'] + g_app_data['app_name'] + 'script'):
		run(host_data['run_script'])

def start_all():
	for host_data in env.hosts:
		start(host_data)

def stop(host_data):
	env.host_string = 'root@' + host_data['name']
	env.password = host_data['password']
	with fabric_op.cd(host_data['deploy_path'] + g_app_data['app_name'] + 'script'):
		run(host_data['stop_script'])

def stop_all():
	for host_data in env.hosts:
		stop(host_data)

def get_lastest_datas(host_data):
	# 1.svn up config file generator code

	# 2.parse datas_desc_xml file 

	# 3.get new data files to the destination folder

	# 4. svn commit the lastest data files
	pass


def test_can_work():
	env.host_string = 'root@192.168.24.159'
	env.password = '123456'
	run('ls')
