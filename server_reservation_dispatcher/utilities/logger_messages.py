def logging_messages(*args, **kwargs):
    if args[0] == 10:
        return "Regex {} fails in output of '{}'".format(kwargs['word'], kwargs['jobname'])
    elif args[0] == 11:
        return "| FAIL | found in output of '{}'".format(kwargs['jobname'])
    elif args[0] == 12:
        return "Suite '{}' was removed from testsWithoutTag file".format(kwargs['suitename'])
    elif args[0] == 13:
        return "| ERROR | found in output of '{}'".format(kwargs['jobname'])
    elif args[0] == 100:
        return "Created new Supervisor object with args: " \
               "jenkins_info = {}, user_info = {}, TLname = {}".format(kwargs['jenkins'],
                                                                       kwargs['user_info'],
                                                                       kwargs['TLname'])
    elif args[0] == 101:
        return "User maximum reservation count exceeded"
    elif args[0] == 102:
        return "Reservation already created"
    elif args[0] == 103:
        return "Reservation failure (Cancelled or Finished)"
    elif args[0] == 104:
        return "Cannot update node in job : {} -> {}".format(kwargs['TLname'], kwargs['jobname'])
    elif args[0] == 105:
        return "Jenkins get job failure"
    elif args[0] == 106:
        return "Jenkins connection error"
    elif args[0] == 107:
        return "Cannot build job '{}'".format(kwargs['jobname'])
    elif args[0] == 108:
        return "Jenkins get console output error"
    elif args[0] == 110:
        return "Matching file name error"
    elif args[0] == 111:
        return "Finding tag in file error"
    elif args[0] == 112:
        return "Cannot open file '{}'".format(kwargs['filename'])
    elif args[0] == 113:
        return "No duration in reseration_data"
    elif args[0] == 114:
        return "Git error"
    elif args[0] == 115:
        return "Reservation created with ID {}".format(kwargs['ID'])
    elif args[0] == 116:
        return "Node in job updated : {} -> {}".format(kwargs['TLname'], kwargs['jobname']),
    elif args[0] == 117:
        return "Cannot get is_queued_or_running status for job '{}'".format(kwargs['jobname'])
    elif args[0] == 118:
        return "Job '{}' was successfully built".format(kwargs['jobname'])
    elif args[0] == 119:
        return "Suite '{}' found in testsWithoutTag file and incremented".format(kwargs['suitename'])
    elif args[0] == 120:
        return "Suite '{}' added to testsWithoutTag file".format(kwargs['suitename'])
    elif args[0] == 124:
        return "Connection to Jenkins failed"
    elif args[0] == 125:
        return "Cannot get job '{}'".format(kwargs['jobname'])
    elif args[0] == 128:
        return "SSH Connection Failure"
    elif args[0] == 129:
        return "'{}' TAG not found in file".format(kwargs['old_tag'])
    elif args[0] == 130:
        return "Critical fail occured, test end status = {}".format(kwargs['test_end_status'])
    elif args[0] == 131:
        return "Suite '{}' failed to start - suite was added to file".format(kwargs['suitename'])
    elif args[0] == 132:
        return "Tag in '{}' changed from '{}' to '{}'".format(kwargs['filename'],
                                                              kwargs['old_tag'],
                                                              kwargs['new_tag']),
    elif args[0] == 133:
        return "Cannot execute 'git pull' command - SSH Error"
    elif args[0] == 134:
        return "Opening FETCH_HEAD file failed"
    elif args[0] == 135:
        return "Cannot get job status '{}'".format(kwargs['jobname'])
    elif args[0] == 136:
        return "Cannot read TLaddress for '{}' from file or file doesn't exists".format(kwargs['TLname'])
    elif args[0] == 1102:
        return "Reservation already exists"
    elif args[0] == 1103:
        return "User max reservation count exceeded"
    elif args[0] == 1104:
        return "Connecting to cloud_ute failure"
    elif args[0] == 1105:
        return "SMPT server failure"
