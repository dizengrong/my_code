import sublime, sublime_plugin
import re, time, threading, os

def FindPreWord(word_list, word):
	pre_word = ""
	for w in word_list:
		if w == word:
			return pre_word
		else:
			pre_word = w
	else:
		return ""
def get_args_num(str):
	index1 = str.find('(')
	index2 = str.find(')')
	substr = str[index1 + 1:index2]
	word_list = re.split(r'\W+', substr)
	args = 0
	for word in word_list:
		if word != '':
			args += 1
	return args
def find_fun_def(view, region_list, function):
	for region in region_list:
		line = view.substr(view.line(region)).strip()
		# print "line: %s" % (line)
		
		if line[0:len(function)] == function and line[-2::] == "->":
			return region
	return False

def get_path(mod):
	if sublime.active_window().folders() != []:
		project_folder = sublime.active_window().folders()[0]
		ret = get_path_help(project_folder, mod)
		return ret
	else:
		base_folder = os.path.dirname(sublime.active_window().active_view().file_name())
		return get_path_help(base_folder, mod)

def get_path_help(base_folder, mod):
	# print "base_folder: %s" % (base_folder)
	rest_folders = []
	for item in os.listdir(base_folder):
		full_path = os.path.join(base_folder, item)
		# print "full_path: %s" % (full_path)
		if os.path.isfile(full_path) and full_path.endswith(".erl"):
			if (mod + ".erl") == item:
				print "return: %s" % (full_path)
				return full_path
		elif os.path.isdir(full_path):
			rest_folders.append(full_path)
	else:
		for item1 in rest_folders:
			ret = get_path_help(item1, mod)
			if ret:
				return ret

def get_line(full_path, mod, function):
	file_handler = open(full_path)
	line_num = 0
	for line in file_handler.readlines():
		line_num += 1
		# print "line_num: %d, line: %s" % (line_num, line)
		try:
			m = re.match(function + "\(.*\)\s{0,}->.*", line.strip())
			if m is not None:
				return line_num
		except:
			continue
	else:
		print "not find"


class ApiJump(sublime_plugin.TextCommand):
	def run(self, edit):
		region = self.view.sel()[0]

		function = self.view.substr(region)
		line = self.view.substr(self.view.line(region.a))

		if ':' + function in line:
			word_list = re.split(r'\W+', line)
			Mod = FindPreWord(word_list, function)
			full_path = get_path(Mod)
		else:
			full_path = self.view.file_name()
			Mod = os.path.basename(full_path)[:-4]

		line = get_line(full_path, Mod, function)
		if line:
			filename = "%s:%d" % (full_path, line)
			sublime.active_window().open_file(filename, sublime.ENCODED_POSITION)


