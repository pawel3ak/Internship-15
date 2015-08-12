"""
doc string...
"""
from multiprocessing.pool import ThreadPool as Pool
from re import compile as recompile
from time import sleep, time
from traceback import format_exc
from subprocess import Popen, PIPE
from xml.etree.cElementTree import ParseError, XML

from utils.jen import jen_rev


# based on BTS_SC_CPLANE/trunk/misc/ci/jobTrigger.xml
FILTERS = [
    (recompile('.'), [
        # .config files (distinguishing between variants
        (recompile(r'(ECL/ECL|\.config_fsmr2)$'), recompile('(.*FSMr2.*(build|bsct|ut|mt).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_fsmr3)$'), recompile('((FDD_|^)FSMr3.*(build(_NoPchs)?|bsct|ut|mt).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*perfGuard.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_tddfsmr3)$'), recompile('((TDD_|^)FSMr3.*(build|bsct|ut|mt).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_fsmr4)$'), recompile('((FDD_|^)(FSMr4|linux_).*(build|bsct|[um]t).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_fzm)$'), recompile('((FDD_|^)FZM.*(build|bsct|ut|mt).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_tddfzm)$'), recompile('((TDD_|^)FZM.*(build|bsct|ut|mt).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_fzc)$'), recompile('((FDD_|^)FZC.*(build|bsct|[um]t).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),
        (recompile(r'(ECL/ECL|\.config_tddfzc)$'), recompile('((TDD_|^)FZC.*(build|bsct|[um]t).*|.*_sct_ccg|.*cpd|.*mcd|.*SHBD.*|.*ttcn3)')),

        # Top-level Makefiles / I_Interface / SC_ISAR (only needed in build and ut jobs)
        (recompile(r'(GNUmakefile|Makefile.local|C_Application/SC_ISAR|I_Interface/Private/Application_Env/Isar_Env/SC_CPlane)'), recompile('.*(CPLANE_build.*|_build(_NoPchs)?|[um]t(_cov|_valgrind|_clang)?|bsct|ttcn3)$')),

        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_Common|C_Test/cplane_k3/src/(Common|SCBM))((?:(?!/Test_modules).)+)$'), recompile('.*((_IPV6)?_(stable|perfGuard)_bsct|_ttcn3)')),
        (recompile(r'(C_Test/cplane_k3/(SCBM|src/Common)|misc/valgrind)'), recompile('.*_sct_valgrind')),

        # build
        (recompile(r'C_Application'), recompile('.*CPLANE_build_(clean|NoPchs)$')),
        (recompile(r'C_Application((?:(?!/Test_modules).)+)$'), recompile('.*CPLANE_build')),
        (recompile(r'(C_Application|T_Tools/SC_CPLANE)((?:(?!/Test_modules).)+)$'), recompile('.*SHBD.*_build')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!)
        (recompile(r'C_Application/SC_Common'), recompile('.*_(ut|build_NoPchs)$')),
        (recompile(r'(C_Application/SC_Common|misc/valgrind)'), recompile('.*_(ut|mt)_valgrind')),
        (recompile(r'C_Test/cplane_k3/src/Common/(types|templates)'), recompile('.*RROM_((ut|mt)$|_valgrind|_clang)')),
        (recompile(r'(C_Application|T_Tools/SC_CPLANE)'), recompile('.*SHBD.*_ut')),

        # pit
        #(recompile(r'(C_Application/SC_Common/Scripts/gencode|C_Test/cplane_k3/src/(Common|SCBM|TestTargets/PIT))'), recompile('.*CPLANE_(man|mem|prf)_(pit|ptt)')),

        # ccg
        (recompile(r'(misc/qcode|C_Test/cplane_k3/src/(Common|SCBM))'), recompile('.*(_(build|sct)_ccg|_ttcn3)')),

        # cpd
        (recompile(r'misc/cpd'), recompile('.*_(cpd|mcd)')),

        # perfGuard_bsct
        (recompile(r'misc/PerformanceGuard'), recompile('.*perfGuard_bsct.*'))
    ]),
    (recompile('CELLC'), [
        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_CELLC|C_Test/cplane_k3/src/TestTargets/CELLC)((?:(?!/Test_modules).)+)$'), recompile('.*CELLC_(stable|perfGuard)_bsct')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/CELLC'), recompile('.*CELLC_sct_valgrind')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!)
        (recompile(r'C_Application/SC_CELLC'), recompile('.*CELLC_(ut(_valgrind)?|mt_valgrind|build_NoPchs)$')),

        # ccg
        (recompile(r'C_Application/SC_CELLC'), recompile('.*_CELLC_build_ccg')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/CELLC'), recompile('.*_CELLC_sct_ccg')),

        # cpd
        (recompile(r'C_Application/SC_CELLC'), recompile('.*CELLC_(cpd|mcd)')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/CELLC'), recompile('.*CELLC_sct_cpd')),
        (recompile(r'(C_Application/SC_CELLC)((?:(?!/Test_modules).)+)$'), recompile('.*CELLC_build_cpd'))
    ]),
    (recompile('ENBC'), [
        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_ENBC|C_Test/cplane_k3/src/TestTargets/ENBC)((?:(?!/Test_modules).)+)$'), recompile('.*ENBC_(stable|perfGuard)_bsct')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/ENBC'), recompile('.*ENBC_sct_valgrind')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!)
        (recompile(r'C_Application/SC_ENBC'), recompile('.*ENBC_(ut(_valgrind)?|mt_valgrind|build_NoPchs)$')),

        # ccg
        (recompile(r'C_Application/SC_ENBC'), recompile('.*_ENBC_build_ccg')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/ENBC'), recompile('.*_ENBC_(sct_(ccg|cpd)|ttcn3)')),

        # cpd
        (recompile(r'C_Application/SC_ENBC'), recompile('.*ENBC_(cpd|mcd)')),
        #(recompile(r'C_Test/cplane_k3/src/TestTargets/ENBC'), recompile('.*ENBC_sct_cpd')),
        (recompile(r'(C_Application/SC_ENBC)((?:(?!/Test_modules).)+)$'), recompile('.*ENBC_build_cpd'))
    ]),
    (recompile('MCEC'), [
        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_MCEC|C_Test/cplane_k3/src/TestTargets/MCEC)((?:(?!/Test_modules).)+)$'), recompile('.*MCEC_(stable|perfGuard)_bsct')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/MCEC'), recompile('.*MCEC_sct_valgrind')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!),
        (recompile(r'C_Application/SC_MCEC'), recompile('.*MCEC_(ut(_valgrind)?|mt_valgrind|build_NoPchs)$')),

        # ccg
        (recompile(r'C_Application/SC_MCEC'), recompile('.*_MCEC_build_ccg')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/MCEC'), recompile('.*_MCEC_(sct_(ccg|cpd)|ttcn3)')),

        # cpd
        (recompile(r'C_Application/SC_MCEC'), recompile('.*MCEC_(cpd|mcd)')),
        #(recompile(r'C_Test/cplane_k3/src/TestTargets/MCEC'), recompile('.*MCEC_sct_cpd')),
        (recompile(r'(C_Application/SC_MCEC)((?:(?!/Test_modules).)+)$'), recompile('.*MCEC_build_cpd'))
    ]),
    (recompile('RROM'), [
        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_RROM|C_Test/cplane_k3/src/TestTargets/RROM)((?:(?!/Test_modules).)+)$'), recompile('.*RROM_(stable|perfGuard)_bsct')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/RROM'), recompile('.*RROM_sct_valgrind')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!)
        (recompile(r'C_Application/SC_RROM'), recompile('.*RROM_(ut(_valgrind)?|mt_valgrind|build_NoPchs)$')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/RROM/NPFs'), recompile('.*RROM_((ut|mt)$|_valgrind|_clang)')),

        # ccg
        (recompile(r'C_Application/SC_RROM'), recompile('.*_RROM_build_ccg')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/RROM'), recompile('.*_RROM_(sct_(ccg|cpd)|ttcn3)')),

        # cpd
        (recompile(r'C_Application/SC_RROM'), recompile('.*RROM_(cpd|mcd)')),
        #(recompile(r'C_Test/cplane_k3/src/TestTargets/RROM'), recompile('.*RROM_sct_cpd')),
        (recompile(r'(C_Application/SC_RROM)((?:(?!/Test_modules).)+)$'), recompile('.*RROM_build_cpd'))
    ]),
    (recompile('TUP[Cc]'), [
        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_TUP/CP_TUPc|C_Test/cplane_k3/src/TestTargets/TUPC)((?:(?!/Test_modules).)+)$'), recompile('.*TUPC(_IPV6)?_(stable|perfGuard)_bsct')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/TUPC'), recompile('.*TUPC_sct_valgrind')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!)
        (recompile(r'C_Application/SC_TUP/CP_TUPc'), recompile('.*TUPC_(ut(_valgrind)?|mt_valgrind|build_NoPchs)$')),

        # ccg
        (recompile(r'C_Application/SC_TUP/CP_TUPc'), recompile('.*_TUPC_build_ccg')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/TUPC'), recompile('.*_TUPC_(sct_(ccg|cpd)|ttcn3)')),

        # cpd
        (recompile(r'C_Application/SC_TUP/CP_TUPc'), recompile('.*TUPC_(cpd|mcd)')),
        #(recompile(r'C_Test/cplane_k3/src/TestTargets/TUPC'), recompile('.*TUPC_sct_cpd')),
        (recompile(r'(C_Application/SC_TUP/CP_TUPc)((?:(?!/Test_modules).)+)$'), recompile('.*TUPC_build_cpd'))
    ]),
    (recompile('UEC'), [
        # (b)sct, sct_valgrind
        (recompile(r'(C_Application/SC_UEC|C_Test/cplane_k3/src/TestTargets/UEC)((?:(?!\/Test_modules).)+)$'), recompile('.*UEC_(stable|perfGuard)_bsct')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/UEC'), recompile('.*UEC_sct_valgrind')),
        (recompile(r'C_Application/SC_CELLC'), recompile('.*CELLC_(ut(_valgrind)?|mt_valgrind)$')),

        # ut, ut/mt_valgrind, ut_clang, cov (started by timer!)
        (recompile(r'C_Application/SC_UEC'), recompile('.*UEC_(ut(_valgrind)?|mt_valgrind|build_NoPchs)$')),

        # ccg
        (recompile(r'C_Application/SC_UEC'), recompile('.*_UEC_build_ccg')),
        (recompile(r'C_Test/cplane_k3/src/TestTargets/UEC'), recompile('.*_UEC_(sct_(ccg|cpd)|ttcn3)')),

        # cpd
        (recompile(r'C_Application/SC_UEC'), recompile('.*UEC_(cpd|mcd)')),
        #(recompile(r'C_Test/cplane_k3/src/TestTargets/UEC'), recompile('.*UEC_sct_cpd')),
        (recompile(r'(C_Application/SC_UEC)((?:(?!/Test_modules).)+)$'), recompile('.*UEC_build_cpd'))
    ])
]


def svn_log(url, cmd=None, username=None, password=None):
    """ Gets data from SVN. """

    try:
        cmd = cmd if isinstance(cmd, list) else [cmd] if cmd else []
        username = ['--username', username] if username else []
        password = ['--password', password] if username and password else []

        log, err = Popen(['svn', 'log', '--xml', '--non-interactive'] \
                         + cmd + username + password + [url],
                         stdout=PIPE, stderr=PIPE).communicate()

        if err:
            raise Exception(err)

        return [{
            'rev':     int(x.attrib['revision']),
            'author':  x.findtext('author'),
            'message': x.findtext('msg') if x.findtext('msg') else '',
            'files':   [(y.text, y.attrib['action']) for y in x.find('paths')] \
                        if x.find('paths') else None
        } for x in XML(log) if x.findtext('author')]

    except ParseError:
        return []



def svn_checker(repos, users, jenks, jobs, queue, options):
    """ Process; checks for changes in repositories. """

    pool = Pool(processes=4)
    debug = options.debug
    ignore = options.ignore_users_filter

    while True:
        try:
            start = time()
            count = 0
            coun2 = 0
            coun3 = 0
            tmp_jobs = {}

            for (url, jenkins) in repos.keys():
                if (url, jenkins) not in repos:
                    continue

                tmp = {}
                # Check if something new
                last = svn_log(url, ['--limit', '1'],
                               repos[(url, jenkins)]['username'],
                               repos[(url, jenkins)]['password'])[0]['rev']

                if (url, jenkins) not in repos:
                    continue

                if last > repos[(url, jenkins)]['revision']:
                    # in this case, get new commits
                    log = svn_log(url, ['--verbose', '--revision', '%d:%d' % \
                        (repos[(url, jenkins)]['revision'] + 1, last)], \
                         repos[(url, jenkins)]['username'], \
                         repos[(url, jenkins)]['password'])

                    for each in log:
                        if debug: # DEBUG ONLY
                            queue.append('-'*125 + '\nSVN: r%d, %s, %s' % (
                                each['rev'], each['author'],
                                each['message'].encode('ascii', 'ignore')))

                        if each['author'] in ['lteulmcpci']:
                            # autoReverts sends to all, clients will filter it
                            for user in [coreid for coreid in users.keys() if \
                                    (url, jenkins) in users[coreid]['repos']]:
                                if user not in tmp:
                                    tmp[user] = []

                                tmp[user].append({
                                    'RepoString': url,
                                    'Revision': each['rev'],
                                    'Author':   each['author'],
                                    'Message':  each['message'],
                                    'PathsChanged':{
                                        'Path':[x for x, y in each['files']]
                                    }
                                })

                                if debug: # DEBUG ONLY
                                    queue.append(' -> %s' % str(user))
                            continue

                        # list of users to sent this commit
                        interested = [coreid for coreid in users.keys() \
                            if (url, jenkins) in users[coreid]['repos'] \
                                and (ignore or \
                                each['author'] in users[coreid]['users'])]

                        if interested:
                            # and check if this run some jobs.
                            if each['files']: # todo ?

                                j = []

                                for file, change in each['files']:

                                    if debug: # DEBUG ONLY
                                        queue.append(' %s  %s' % \
                                            (change, file))

                                    if change == 'D' or jenkins not in jenks:
                                        continue

                                    for module, rest in FILTERS:
                                        if module.search(file):
                                            for path, exp in rest:

                                                if not path.search(file):
                                                    continue

                                                for job in jenks[jenkins].keys():
                                                    if job in j:
                                                        continue
                                                    elif exp.search(job):
                                                        j.append(job)
                                    coun3 += 1

                                commit = {
                                    'RepoString': url,
                                    'Revision': each['rev'],
                                    'Author': each['author'],
                                    'Message': each['message'].encode('ascii', 'ignore'),
                                    'PathsChanged': {
                                        'Path': [x for x, y in each['files']]
                                    }
                                }

                                if j and jenkins in jenks:
                                    job_list = pool.map(jen_rev, [(jenks[jenkins][x], each['rev'])
                                                              for x in jenks[jenkins].keys() if x in j]) # todo fix

                                    if job_list:
                                        if debug: # DEBUG ONLY
                                            queue.append(' '*4 + '- '*60)
                                            queue.extend(['    {:<31} {}'.format(job_name, job_url) for job_name, job_url in job_list])

                                        commit['Jobs'] = {'Job': [{
                                            'URL': job_url,
                                            'Name': job_name,
                                            'Status': 'NONE'
                                        } for job_name, job_url in job_list]}

                                        for job_name, job_url in job_list:
                                            if (each['rev'], job_url) in tmp_jobs:
                                                temp = tmp_jobs[(each['rev'], job_url)]
                                                temp['users'] = list(temp['users'] + interested)
                                                tmp_jobs[(each['rev'], job_url)] = temp
                                            else:
                                                tmp_jobs[(each['rev'], job_url)] = {
                                                    'name': job_name,
                                                    'state': 'NONE',
                                                    'users': interested
                                                }

                                for user in interested:
                                    if user not in tmp:
                                        tmp[user] = []

                                    tmp[user].append(commit)

                                    if debug: # DEBUG ONLY
                                        queue.append(' -> %s' % str(user))

                            if debug: # DEBUG ONLY
                                coun2 += 1

                    if (url, jenkins) not in repos:
                        continue

                    # and update local "database".
                    temp = repos[(url, jenkins)]
                    temp['revision'] = last
                    repos[(url, jenkins)] = temp

                if debug: # DEBUG ONLY
                    count += 1

                if tmp:
                    queue.extend([(users[user]['socket'], {
                            'Commits': {'Commit': tmp[user]}}
                        ) for user in tmp.keys() if user in users])

            if tmp_jobs:
                for job in tmp_jobs.keys():
                    if job in jobs:
                        temp = jobs[(each['rev'], job_url)]
                        temp['users'] = list(temp['users'] + interested)
                        jobs[(each['rev'], job_url)] = temp
                    else:
                        jobs[job] = tmp_jobs[job]

            if debug: # DEBUG ONLY
                queue.append('^svn: %f[s] (%d/%d/%d)' \
                             % (time() - start, count, coun2, coun3))

            delta = time() - start
            sleep(10 - delta if delta < 10 else 0.1)

        except Exception, exc:
            if debug: # DEBUG ONLY
                queue.append(format_exc(exc))
