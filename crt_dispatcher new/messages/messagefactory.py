"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
from internalmessage import MessageCloner, InternalMessage
from class_loader import Class_Loader

__author__ = 'gtqk84 Michal Plichta'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-12-14'
__maintainer__ = 'gtqk84 Michal Plichta'
__email__ = 'gtqk84@nokia.com'


class MessageFactory(object):
    def __init__(self):
        self.msg_cloner = MessageCloner()

    def get_msg(self, serialized_payload):
        self.msg_cloner.deserialize(payload=serialized_payload)
        (module_name, class_name) = self.msg_cloner.msg_type.split('.')
        package_name = ".".join(self.msg_cloner.__class__.__module__.split('.')[:-1])
        try:
            msg = Class_Loader.load_instance({'CLASS': '%s.%s.%s' % (package_name, module_name, class_name),
                                              'CONSTRUCTOR_PARAMETERS': dict(self.msg_cloner)})
        except ImportError:  # required to not crash app on unknown message receival
            msg = InternalMessage(self.msg_cloner)

        return msg
