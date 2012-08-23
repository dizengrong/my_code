from xml.dom import minidom

def get_attrvalue(node, attrname):
	return node.getAttribute(attrname) if node else ''

def get_nodevalue(node, index = 0):
	return node.childNodes[index].nodeValue if node else ''

def get_xmlnode(node, name):
	return node.getElementsByTagName(name) if node else []

def load_file(filename = 'servers.xml'):
    doc         = minidom.parse(filename)
    root        = doc.documentElement

    server_nodes  = get_xmlnode(root, 'server')
    servers   = []
    for node in server_nodes:
        ip       = get_nodevalue(get_xmlnode(node, 'ip')[0])
        password = get_nodevalue(get_xmlnode(node, 'password')[0])
        server = {'ip': ip,
                  'password': password}
        servers.append(server)
    return servers
        