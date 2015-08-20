"""
:created on: '20/08/15'

:copyright: Nokia
:author: Damian Papiez
:contact: damian.papiez@nokia.com
"""


# update record in dictionary
def update_record(dictionary, server_id, reservation_id=None, busy_status=None,
                  time_add=None, duration=None, tl_name=None, job_test_status=None):
    if reservation_id is not None:
        dictionary[server_id]["handle"] = reservation_id
    if busy_status is not None:
        dictionary[server_id]["handle"] = busy_status
    if time_add is not None:
        dictionary[server_id]["handle"] = time_add
    if duration is not None:
        dictionary[server_id]["handle"] = duration
    if tl_name is not None:
        dictionary[server_id]["handle"] = tl_name
    if job_test_status is not None:
        dictionary[server_id]["handle"] = job_test_status


# Get first not busy tl
def get_first_not_busy(dictionary):
    for record in dictionary:
        if dictionary[record]['busy_status'] == False:
            return record["server_id"]
    return None
