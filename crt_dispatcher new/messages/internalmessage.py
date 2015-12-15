"""
CRT Dispatcher website:
https://confluence.int.net.nokia.com/display/RUFF/CRT+Dispatcher
"""
import json
from crt_dispatcher.exeptions import IncompatibleMsgVersion

__author__ = 'gtqk84 Michal Plichta'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-12-07'
__maintainer__ = 'gtqk84 Michal Plichta'
__email__ = 'gtqk84@nokia.com'


class InternalMessage(dict):
    def serialize(self):
        msg_dict = self._append_metadata_keys(self)
        return self._dict2serialization_format(msg_dict)

    def deserialize(self, payload):
        msg_dict = self._serialization_format2dict(payload)
        self._remove_old_keys(msg_dict)
        self._copy_new_dict(msg_dict)
        self._ignore_metadata_keys()

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __repr__(self):
        base_dump = super(InternalMessage, self).__repr__()
        return "{}({})".format(self.__class__.__name__, base_dump)

    def _remove_old_keys(self, new_keys):
        for key in self:
            if key not in new_keys:
                self.pop(key)

    def _copy_new_dict(self, new_dict):
        for key in new_dict:
            self[key] = new_dict[key]

    def _append_metadata_keys(self, data_dict):
        msg_dict = dict(data_dict)
        class_name = self.__class__.__name__
        module_name = self.__class__.__module__.split('.')[-1]
        msg_dict['msg_type'] = "{}.{}".format(module_name, class_name)
        return msg_dict

    def _ignore_metadata_keys(self):
        self.pop('msg_type', None)

    # only below we see that serialization format is JSON
    @staticmethod
    def _dict2serialization_format(msg_dict):
        return json.dumps(msg_dict)

    @staticmethod
    def _serialization_format2dict(payload):
        return json.loads(payload)


class MessageCloner(InternalMessage):
    """ This class is used during deserialization process
    It handles msg_type metadata
    Thanks to this MessageFactory is unaware of serialization format - it only uses msg_type
    """
    def __init__(self, *arg, **kwargs):
        super(MessageCloner, self).__init__(*arg, **kwargs)
        self.msg_type = self.pop('msg_type', None)  # may not be present

    def _copy_new_dict(self, new_dict):
        super(MessageCloner, self)._copy_new_dict(new_dict)
        # take metadata before base class will throw it away
        self.msg_type = self['msg_type']  # must be present

    def __repr__(self):
        base_dump = super(MessageCloner, self).__repr__()
        msg_class = self.__class__.__name__
        msg_type = self.msg_type
        return "{}:{}({})".format(msg_type, msg_class, base_dump)
