import erldet, urllib
from fabric.api import env, run, cd
from fabric import operations as fabric_op
from xml.dom import minidom

g_server      = '192.168.24.159'
g_password    = '123456'
g_deploy_path = '/home/samba/sg/'
g_script_path = '/home/samba/sg/script/'
g_start_sh    = './sg_ctrl.sh start'
g_stop_sh     = './sg_ctrl.sh stop'
g_status_sh     = './sg_ctrl.sh status'
g_make_sh	  = './sg_ctrl.sh make'
g_datas_config = {'svn_path': '/home/web/service/ConfigFileGenerator/',
				  'datas_desc_xml': '/home/web/service/ConfigFileGenerator/config/DataConfig.xml',
				  'save_path': '/home/samba/sg/src/data/',
				  'gen_data_url': 'http://192.168.24.159:159/ConfigFileGenerator/main/gen_data_file.php',
				  'get_data_url': 'http://192.168.24.159:159/ConfigFileGenerator/data/'}

def set_host():
	env.host_string = 'root@' + g_server
	env.password    = g_password

def run_cmd(cmd):
	with cd(g_script_path): 
		run(cmd)	

def start():
	status = get_status()
	if status == 2:
		print("server is in running...\n")
	else:
		if status == 1:
			stop()
		set_host()
		run_cmd(g_start_sh)

def stop():
	set_host()
	run_cmd(g_stop_sh)

def make():
	set_host()
	run_cmd(g_make_sh)

# return:
# 2: alive, 1: something wrong, 0: die 
def get_status():
	set_host()
	run_cmd(g_status_sh)
	fabric_op.get('/tmp/result_tmp_file', 'server_status')
	fd = open('server_status')
	alive_times = 0
	for each_line in fd:
		if '[alive]' in each_line:
			alive_times += 1
	if alive_times == 2:
		return 2
	elif alive_times == 1:
		return 1
	else:
		return 0

def get_lastest_datas():
	set_host()
	# 1.svn up config file generator code
	with cd(g_datas_config['svn_path']): 
		run('svn up')

	# 2.parse datas_desc_xml file
	data_files = get_all_filename_from_xml()

	# 3.get new data files to the destination folder
	for data_file in data_files:
		urllib.urlopen(g_datas_config['gen_data_url'] + '?file=' + data_file)
		get_url = g_datas_config['get_data_url'] + data_file + '.erl'
		run('wget -O ' + g_datas_config['save_path'] + data_file + '.erl ' + get_url)

	# 4. svn commit the lastest data files
	with cd(g_deploy_path): 
		run('svn ci -m \'update datas file from php\' ' + g_datas_config['save_path'])

def get_all_filename_from_xml(remote_xml_file = g_datas_config['datas_desc_xml']):
	fabric_op.get(remote_xml_file, 'datas_xml_file.xml')

	doc        = minidom.parse('datas_xml_file.xml')
	root       = doc.documentElement
	file_nodes = erldet.get_xmlnode(root, 'file')
	data_files = []
	for file_node in file_nodes:
		erl_mod = erldet.get_attrvalue(file_node, 'mod_name')
		data_files.append(erl_mod)

	return data_files


def test_can_work():
	env.host_string = 'root@192.168.24.159'
	env.password = '123456'
	with cd('/home/samba/sg'): 
		run('ls -a')