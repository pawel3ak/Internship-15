# import json
# from jenkinsapi.api import Jenkins
# # from jenkins import Jenkins
# import signal
#
# path = "/home/ute/PycharmProjects/projekty/Internship-15/server_reservation_dispatcher/utilities/TL_name_to_address_map.data"
#
# def create_TL_name_to_address_map_from_file_output(TL_map_file):
#         TL_map = {}
#         [TL_map.update(json.loads(line)) for line in TL_map_file.readlines() if not line == '']
#         return TL_map
#
# def delete_TL_address_from_TL_map_file(TLname):
#     with open(path, 'rb+') as TL_map_file:
#             TL_map = create_TL_name_to_address_map_from_file_output(TL_map_file)
#             if TLname in TL_map:
#                 TL_map.pop(TLname)
#             for tl in TL_map:
#                 print tl
#             # [TL_map_file.writelines(json.dumps({TLname : TL_map[TLname]}) + "\n") for TLname in TL_map]
#
# # delete_TL_address_from_TL_map_file("IAV_WRO_CLOUD113")
# # j = Jenkins('http://10.159.74.18:8080', username='crt', password='Flexi1234')
# # def raise_timeout():
# #     signal.alarm(0)
# #
# # signal.alarm(10)
# # signal.signal(signal.SIGALRM, raise_timeout)
#
# # job = j.build_job("test_on_tl99_test",params={"name":"LTEXYZ"})
#
import sys
functions_with_warning = {
    'def delete_file_with_basic_info(self):', 99999,





                         }

functions_with_error = {

}

functions_with_critical = {
    'set_node_for_job' : {
        'status' : 'JenkinsError', 'number' : 104
    },
    'get_job_status' : {

    }
}
func_name_to_error = {'pierwsza' : 125,
                      'druga' : 133}
#
# def probowanie(func):
#     def trajing(*args, **kwargs):
#         for _ in range(5):
#             try:
#                 return func(_, *args, **kwargs)
#             except:
#                 print _
#                 # print func_name_to_error[func.__name__]
#         return finish(func.__name__)
#     return trajing
#
#
# @probowanie
# def pierwsza(*args, **kwargs):
#     # print melodia
#     # print 2*2
#     if args[0] == 5:
#         print "dwa"
#     else:
#         print 3/0
#
# def finish(*args, **kwargs):
#     print args[0]
#     sys.exit(1)
#
#
# pierwsza(1, 5)
#
#
# def fff(*args, **kwargs):
#     return
#
#
# print fff(jenkins="abc")
#
# with open("/home/ute/PycharmProjects/projekty/Internship-15/server_reservation_dispatcher/files/SuperVisor/testsWithoutTag.txt", "rb") as ff:
#     import time
#     time.sleep(30)
def a():
    return 0, 0

print a()

#
# jenkins_job_info = {
#             'parameters' : {
#                 'name' : 'LTEXYZ'
#             }
#     }
# user_info = {
#     'first_name' : 'Pawel',
#     'last_name' : 'Nogiec',
#     'mail' : 'pawel.nogiec@nokia.com'
# }
#
#
# from superVisor_api import SuperVisor
#
#
# superVisor_api = SuperVisor('tl99_test', jenkins_job_info, user_info)

