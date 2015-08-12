# -*- coding: utf-8 -*-
"""
:created on: '10/8/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""


class XmlConfigApiException(Exception):
    """Base XmlConfigApiException."""

class XmlConfigApiFailValidationArgumentsException(XmlConfigApiException):

    def __init__(self, name, number):
        self.name = name
        self.number = number
    def __str__(self):
        return "Not enough parameters in '{name}[{number}]'".format(name=self.name, number=self.number)

class XmlConfigApiUnknownPathException(Exception):
    def __init__(self,message):
        self.message=message
        pass
    def __str__(self):
        return self.message

