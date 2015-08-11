# -*- coding: utf-8 -*-
"""
:created on: '10/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com, pawel.nogiec@nokia.com
"""

import xml.etree.ElementTree as ET
INTERNSHIP_PATH = "/home/ute/PycharmProjects/projekty/Internship-15/_jenkins/"
EMPTY_CONFIG_XML_PATH = "/home/ute/PycharmProjects/projekty/Internship-15/_jenkins/empty_config_file.xml"
TASKS = {
    0 : 'hudson.tasks.Shell',                               #shell command
    1 : 'hudson.plugins.python.Python', #python script
    2 : 'hudson.tasks.BatchFile',                           #windows batch command
}
PARAMETERS = {
    0 : 'hudson.model.StringParameterDefinition',   # string
    1 : 'hudson.model.BooleanParameterDefinition',  # boolean
    2 : 'hudson.model.RunParameterDefinition',      # run
    3 : 'hudson.model.TextParameterDefinition',     # text
}
command_to_execute = 'python /home/ute/tests/test_job.py $f_name'

class XML_config(object):
    def __init__(self, path):
        self.path = path
        self.tree = self.get_tree(self.path)
        scm_tag = self.tree.find('scm')
        scm_tag.set('class','hudson.scm.NullSCM')


    def get_tree(self,path):
        try:
            self.tree = ET.parse(path)
            self.update_path(path)
            return self.tree
        except OSError as e:
            print e.message

    def update_tree(self,tree):
        self.tree = tree
        return self.tree

    def get_path(self):
        if not self.path == None:
            return self.path
        else:
            pass
            #raise Exception.message

    def update_path(self,path):
        self.path = path
        return self.path

    def _add_task(self,_type,command_to_execute):

        builders_tag = self.tree.find('builders')
        builders_tag.text = "\n\t"
        task_tag = ET.SubElement(builders_tag, TASKS[_type])
        if _type == 1:      #python script
            task_tag.set('plugin', 'python@1.2')
        task_tag.text = "\n\t\t"
        command_tag = ET.SubElement(task_tag,'command')
        command_tag.text = command_to_execute
        command_tag.tail = "\n\t"
        task_tag.tail = "\n  "
        return self.update_tree(self.tree)

    def _add_parameter(self, _parameter):
        if not len(_parameter) == 4:
            #raise
            print 'Not enough parameters'
            return
        properties_tag = self.tree.find('properties')
        properties_tag.text = '\n\t'
        parametersDefinitionProperty = ET.SubElement(properties_tag, 'hudson.model.ParametersDefinitionProperty')
        parametersDefinitionProperty.text = '\n\t\t'
        parameterDefitnitions = ET.SubElement(parametersDefinitionProperty, 'parameterDefinitions')
        parameterDefitnitions.text = '\n\t\t\t'
        parameter_tag = ET.SubElement(parameterDefitnitions, PARAMETERS[_parameter['type']])
        parameter_tag.text = '\n\t\t\t\t'
        name_tag = ET.SubElement(parameter_tag, 'name')
        name_tag.text = _parameter['name']
        desciption_tag = ET.SubElement(parameter_tag, 'desciption')
        desciption_tag.text = _parameter['description']
        default_value_tag = ET.SubElement(parameter_tag, 'default_value')
        default_value_tag.text = _parameter['default_value']
        name_tag.tail = '\n\t\t\t\t'
        desciption_tag.tail = '\n\t\t\t\t'
        default_value_tag.tail = '\n\t\t\t'
        parameter_tag.tail = '\n\t\t'
        parameterDefitnitions.tail = '\n\t'
        parametersDefinitionProperty.tail = '\n  '
        return self.update_tree(self.tree)

    def _assigned_node(self, name):
        root = self.tree.getroot()
        assignedNode = ET.Element('assignedNode')
        assignedNode.text = str(name)
        assignedNode.tail = '\n  '
        root.insert(3,assignedNode)
        return self.update_tree(self.tree)

    ###temporary function
    def write_tree(self,xml_file_path):
        try:
            self.tree.write(xml_file_path)
            return xml_file_path
        except OSError as e:
            print e.message





if __name__ == "__main__":
    xml = XML_config(EMPTY_CONFIG_XML_PATH)
    xml._add_task(0,command_to_execute)
    xml._add_task(0,command_to_execute)

    parameters = {'type': 0,
                  'name': 'f_name',
                  'description': '',
                  'default_value': '3'}

    xml._add_parameter(parameters)
    parameters['default_value'] = 'inna'
    xml._add_parameter(parameters)
    xml._assigned_node("tl_wroc")
    xml.write_tree(INTERNSHIP_PATH + "output.xml")
    pass





