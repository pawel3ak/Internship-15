# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'
:version: '30/09/15'
:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""


from superVisor_api import SuperVisor

def supervise(TLname, jenkins_job_info, user_info = None):

    superVisor_api = SuperVisor(TLname, jenkins_job_info, user_info)
    superVisor_api.make_file_with_basic_info()
    superVisor_api.set_job()
    if not superVisor_api.is_queued_or_running(once = True):
        superVisor_api.set_node_for_job()
        superVisor_api.build_job()
    superVisor_api.is_queued_or_running()
    superVisor_api.check_job_status()
    if superVisor_api.get_job_status() == "SUCCESS":
        superVisor_api.remove_tag_from_testsWithoutTag_file_if_tag_is_in_suite()
        superVisor_api.divide_job_output_into_suite_and_golden_part()
        superVisor_api.parse_output_and_set_job_failed_tests(output_name="suite")
        superVisor_api.add_disable_tag_to_robot_tests_files()
    superVisor_api.send_information_about_executed_job()
    if not superVisor_api.parse_output_and_set_job_failed_tests(output_name="golden"):
        superVisor_api.send_information_about_executed_job(send_to_admin=True)
