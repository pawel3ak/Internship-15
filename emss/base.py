# -*- coding: utf-8 -*-
'''
:author: Jan Galda
:contact: jan.galda@nsn.com
'''
from ruff.devices.emss import EMSsim
from ruff.devices import devicemanager
from ruff import handler

from ..utilities.EmssAttribute import transform_dict_of_attributes_to_emss_input_list


class EMSSInterface(object):
    def __init__(self, emssim_name="emss", host=None, port=None):
        '''
        EMSsim interface used EMSsim device to perform commands on it

        Requires IP (host/port) where EMSsim tool serves it's JSON-RPC interface
        You can take this parameters from EMSsim console via command:

        json_svr

        |========================================================|
        | NAME |           INTERFACE            | PORT | CLIENTS |
        |========================================================|
        | emssj| emssim-2.krk-lab.nsn-rdnet.net | 4037 |   ---   |
        |--------------------------------------------------------|
        '''
        self.emss_name = emssim_name
        self.emss_host = host
        self.emss_port = port
        self.emssim = None

    def __del__(self):
        self._terminate_emss_instance()

    def get_emssim_command(self, command):
        '''Gets EMSsim command object for further processing

        :param command: name of EMSsim command
        : returns     :  EMSsim command object

        +---------------------------------+----------------------------+-----------------+
        |                                       Examples                                 |
        +=================================+============================+=================+
        | ${cmd_obj}=  get EMSsim command |  bts_connection_status                       |
        | ${run_ok}=   Call Method        |  ${cmd_obj}   run           timeout=30       |
        | ${status}=   Call Method        |  ${cmd_obj}   get status                     |
        | Should Be Equal As Strings      |  ${status}    Status.SUCCESS                 |
        | ${started}=  Call Method        |  ${cmd_obj}   start                          |
        | Call Method                     |  ${cmd_obj}   await finish  timeout=30       |
        +---------------------------------+----------------------------+-----------------+
        '''
        # find command method inside device emssim
        if command[:4] != 'cmd_':
            command = 'cmd_' + command
        cmd_method = getattr(self.emssim, command)
        #TODO: put more detailed info into Robot logs if command not found?
        cmd_object = cmd_method()
        return cmd_object

    def run_emssim_command(self, command, params=None):  # TODO how to pass **kwparams
        '''Runs EMSS command

        :param command: name of EMSS command or variable holding command object
        :param params:  parameters of the command (optional, default = None), can be string or array

        +--------------------------------+----------------------------+-----------------+
        |                                       Examples                                |
        +================================+============================+=================+
        | ${result}=  run EMSsim command |  cmd_bts_connection_status |                 |
        +--------------------------------+----------------------------+-----------------+
        | ${result}=  run EMSsim command |  bts_connection_status     |                 |
        +--------------------------------+----------------------------+-----------------+
        | ${cmdobj}=  get EMSsim command |  bts_connection_status     |                 |
        | ${result}=  run EMSsim command |  ${cmdobj}                 |                 |
        +--------------------------------+----------------------------+-----------------+
        | ${result}=  run EMSsim command |  xxxx                      |   params        |
        +--------------------------------+----------------------------+-----------------+
        '''
        # get command object, run it, check that run was OK
        if isinstance(command, handler.DataHandler):
            cmd_object = command
        else:
            cmd_object = self.get_emssim_command(command)
        assert (cmd_object.run(params))  # run() returns True on SUCCESS
        # return result of this command
        return cmd_object.returned_data()

    def _case_insensitive_stings_comparison(self, string1, string2):
        return str(string1).lower() == str(string2).lower()

    def enb_configuration_should_be_discovered(self):
        '''Fails if BTS has not been discovered yet

        +----------------------------------------+
        |                Examples                |
        +========================================+
        | enb configuration should be discovered |
        +----------------------------------------+
        '''
        c_status = self.emssim.cmd_bts_connection_status()
        c_status.run()
        ret = c_status.returned_data()
        assert (ret['discover_status']), "eNB is not discovered"  # TODO: assert may be switched off by python -O

    def terminate_emss_instance(self):
        """
        Method to decorate _terminate_emss_instance (which removes ta_emss object from register)
        :return: None
        """
        print("ta_emss: do not use terminate_emss_instance directly, ta_emss is terminated in its destructor.")

    def _terminate_emss_instance(self):  # TODO: consult neccessity of this resolution
        '''Stops threads started by emss
        '''
        self.emssim = None
        devicemanager.remove_device_from_registry(self.emss_name)

    def _log2robotconsole(self, msg, debug=1):  # TODO : THIS METHOD IS USED ONLY FOR DEBUGGING
        if debug:
            from robot.api import logger
            logger.console("\n" + msg + "\n")

    def _format_comma_or_space_separated_string_given_by_user(self, comma_or_space_separated_string):
        assert isinstance(comma_or_space_separated_string, basestring), "%s has to be a string" % comma_or_space_separated_string

        if "," in comma_or_space_separated_string:
            output_list = str(comma_or_space_separated_string).replace(" ", "").split(",")
        else:
            output_list = str(comma_or_space_separated_string).split()
        return output_list

    def _parse_edit_params(self, object, dict_of_attributes):
        list_of_params = [object]
        list_of_params.extend(transform_dict_of_attributes_to_emss_input_list(dict_of_attributes))
        return " ".join(list_of_params)
