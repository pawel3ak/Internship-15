# -*- coding: utf-8 -*-
"""
:created on: '10/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nsn.com, pawel.nogiec@nokia.com
"""

import xml.etree.ElementTree as ET

from _jenkins.xml_config_api.exceptions import *


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
        canRoam_tag = self.tree.find('canRoam')
        canRoam_tag.text = 'false'


    def get_tree(self,path):
        try:
            self.tree = ET.parse(path)
            self.update_path(path)
            return self.tree
        except IOError as e:
            raise XmlConfigApiException(e)

    def update_tree(self,tree):
        self.tree = tree
        return self.tree

    def get_path(self):
        try:
            return self.path
        except AttributeError as e:
            raise XmlConfigApiUnknownPathException(e.message)



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

        for param_number in range(0,len(_parameter)):
            if not len(_parameter[param_number]) == 4:
                raise XmlConfigApiFailValidationArgumentsException("_parameter",param_number)

        properties_tag = self.tree.find('properties')
        properties_tag.text = '\n\t'
        parametersDefinitionProperty = ET.SubElement(properties_tag, 'hudson.model.ParametersDefinitionProperty')
        parametersDefinitionProperty.text = '\n\t\t'
        parameterDefitnitions = ET.SubElement(parametersDefinitionProperty, 'parameterDefinitions')
        parameterDefitnitions.text = '\n\t\t\t'
        parameterDefitnitions.text = '\n\t\t\t'
        for param_number in range(0,len(_parameter)):
            parameter_tag = ET.SubElement(parameterDefitnitions, PARAMETERS[_parameter[param_number]['type']])
            parameter_tag.text = '\n\t\t\t\t'
            name_tag = ET.SubElement(parameter_tag, 'name')
            name_tag.text = _parameter[param_number]['name']
            desciption_tag = ET.SubElement(parameter_tag, 'desciption')
            desciption_tag.text = _parameter[param_number]['description']
            defaultValue_tag = ET.SubElement(parameter_tag, 'defaultValue')
            defaultValue_tag.text = _parameter[param_number]['defaultValue']
            name_tag.tail = '\n\t\t\t\t'
            desciption_tag.tail = '\n\t\t\t\t'
            defaultValue_tag.tail = '\n\t\t\t'
            parameter_tag.tail = '\n\t\t\t'
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
    xml._add_task(0,command_to_execute[:-7] + str('$plik'))
    parameters =[]
    parameters.append({'type': 0,
                  'name': 'f_name',
                  'description': '',
                  'defaultValue': '2'})
    parameters.append({'type': 0,
                  'name': 'plik',
                  'description': '',
                  'defaultValue': 'cos'})
    xml._add_parameter(parameters)
    #parameters['default_value'] = 'inna'
    #xml._add_parameter(parameters)
    xml._assigned_node("moj_dwa")
    xml.write_tree(INTERNSHIP_PATH + "output.xml")






