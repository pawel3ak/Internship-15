# -*- coding: utf-8 -*-
"""
:created on: '11/08/15'

:copyright: Nokia
:author: Pawel Nogiec
:contact: pawel.nogiec@nokia.com
"""


from superVisor_api import SuperVisor

def supervise(TLname, jenkins_job_info, user_info = None):
    superVisor_api = SuperVisor(TLname, jenkins_job_info, user_info)
    superVisor_api.make_file_with_basic_info()
    superVisor_api.set_jenkins_connection()
    superVisor_api.set_job_handler()
    if not superVisor_api.is_queued_or_running(once = True):
        superVisor_api.set_node_for_job()
        superVisor_api.build_job()
    superVisor_api.is_queued_or_running()
    superVisor_api.set_job_status()
    superVisor_api.check_job_status()
    # superVisor_api.set_job_status()
    # superVisor_api.check_job_status()
    if superVisor_api.get_job_status() == "SUCCESS":
        superVisor_api.remove_tag_from_testsWithoutTag_file_if_tag_is_in_suite()
        superVisor_api.set_jenkins_console_output()
        superVisor_api.parse_output_and_set_job_failed_tests()
        superVisor_api.remove_tag_from_robots_tests()
    superVisor_api.send_information_about_executed_job()
    superVisor_api.delete_file_with_basic_info()


if __name__ == '__main__':
    import os

    dirs = [dir for dir in os.listdir("/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/") if os.path.isdir(os.path.join("/home/ute/auto/ruff_scripts/testsuite/WMP/CPLN/", dir))]


    jenkins_job_info = {
            'parameters' : {
                'name' : 'LTEXYZ'
            }
    }
    user_info = {
        'first_name' : 'Pawel',
        'last_name' : 'Nogiec',
        'mail' : 'pawel.nogiec@nokia.com'
    }
    for dir in dirs:
        if dir == "LTE2465" or dir == "LTE2351" or dir == "LTE1819": continue
        import multiprocessing
        jenkins_job_info = {
            'parameters' : {
                'name' : "LTEXYZ"
            }
        }
        # print dir
        process = multiprocessing.Process(target=supervise, args=['tl99_test',jenkins_job_info, user_info])
        process.start()
        process.join()
        print "Finishing dir %s" % (dir)
        # supervise('tl99_test', jenkins_job_info, user_info)

