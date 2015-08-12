"""
module docstrng...
"""
from xml.dom.minidom import Document, parseString
import copy

class DictToXml(object):
    """ dict2xml from http://pynuggets.wordpress.com/2011/06/06/dict2xml-4/ """

    def __init__(self, structure):
        """ doc string... """

        self.doc = Document()
        if len(structure) == 1:
            root_name = str(structure.keys()[0])
            self.root = self.doc.createElement(root_name)
            self.doc.appendChild(self.root)
            self.build(self.root, structure[root_name])

    def __str__(self):
        """ doc string... """

        return self.doc.toxml()

    def display(self):
        """ doc string... """

        print self.pretty()

    def pretty(self):
        """ doc string... """

        return self.doc.toprettyxml(indent='    ', newl='\r\n')

    def build(self, father, structure):
        """ doc string... """

        if type(structure) == dict:
            for key in structure:
                tag = self.doc.createElement(key)
                father.appendChild(tag)
                self.build(tag, structure[key])

        elif type(structure) == list:
            grand_father = father.parentNode
            uncle = copy.deepcopy(father)
            for key in structure:
                self.build(father, key)
                grand_father.appendChild(father)
                father = copy.deepcopy(uncle)

        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)


class NotTextNodeError(Exception):
    """ doc string... """
    pass


def get_text_from_node(node):
    """
    scans through all children of node and gathers the
    text. if node has non-text child-nodes, then
    NotTextNodeError is raised.
    """
    txt = u""
    for tmp in node.childNodes:
        if tmp.nodeType == tmp.TEXT_NODE:
            txt += tmp.nodeValue
        else:
            raise NotTextNodeError
    return txt


def node_to_dic(node):
    """
    nodeToDic() scans through the children of node and makes a
    dictionary from the content.
    three cases are differentiated:
	- if the node contains no other nodes, it is a text-node
    and {nodeName:text} is merged into the dictionary.
	- if the node has the attribute "method" set to "true",
    then it's children will be appended to a list and this
    list is merged to the dictionary in the form: {nodeName:list}.
	- else, nodeToDic() will call itself recursively on
    the nodes children (merging {nodeName:nodeToDic()} to
    the dictionary).
    """
    dic = {}
    multlist = {} # holds temporary lists where there are multiple children
    multiple = False
    for tmp in node.childNodes:
        if tmp.nodeType != tmp.ELEMENT_NODE:
            continue

        # find out if there are multiple records
        if len(node.getElementsByTagName(tmp.nodeName)) > 1:
            multiple = True
            # and set up the list to hold the values
            if not multlist.has_key(tmp.nodeName):
                multlist[tmp.nodeName] = []

        try:
            #text node
            text = get_text_from_node(tmp)
        except NotTextNodeError:
            if multiple:
                # append to our list
                multlist[tmp.nodeName].append(node_to_dic(tmp))
                dic.update({tmp.nodeName:multlist[tmp.nodeName]})
                continue
            else:
                # 'normal' node
                dic.update({tmp.nodeName:node_to_dic(tmp)})
                continue

        # text node
        if multiple:
            multlist[tmp.nodeName].append(text)
            dic.update({tmp.nodeName:multlist[tmp.nodeName]})
        else:
            dic.update({tmp.nodeName:text})
    return dic

def xml2dict(filename):
    """ xml2dict from http://code.activestate.com/recipes/116539/ """

    dom = parseString(filename)
    return node_to_dic(dom)
