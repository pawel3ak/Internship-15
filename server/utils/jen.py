"""
module docstring...
"""
from multiprocessing.pool import ThreadPool as Pool
from time import sleep, time
from traceback import format_exc
from urllib2 import urlopen


RUNNING = 'RUNNING'
DELETE = 'DELETE'
NONE = 'NONE'


def jen_exe(url):
    """ Gets data from Jenkins. """

    found = url.find('/api')
    if found != -1:
        url = url[0:found]

    try:
        resp = urlopen(url.strip('/') + '/api/python/').read()
        return eval(resp)
    except Exception:
        return None


def jen_job(rev, url=None, old_url=None):
    """
    Gets job's (rev, url, state, old_url) in Jenkins.
    Available states: NONE, RUNNING. FAILED, UNSTABLE, SUCCESS, DELETE
    """

    from re import search

    try:
        rev, url = rev
    except Exception:
        pass

    if url is None:
        return None

    url = url.strip('/')
    state = jen_exe(url)

    if not (state and state['changeSet']['kind']):
        # job still not in queue
        return (rev, url, NONE, old_url)

    if  len(state['changeSet']['items']) > 0:
        commits = [item['revision'] for item in state['changeSet']['items']]
        commits.sort()

        if rev in commits:
            # everything seems ok
            if not old_url and 'lastBuild' in url:
                old_url = url
                reg = search(r'^(https?:\/\/[^\/]+\/job\/([^\/]+))\/?([0-9]+)?\/?', old_url)
                url = reg.group(1) + ('/%d' % state['number'])

            return (
                rev, url, RUNNING if state['building'] else state['result']
                if state['result'] else NONE, old_url)

        if rev < commits[-1]:
            # job not triggered to this commit
            return (rev, url, DELETE, old_url)

    #reg = search(r'^(https?:\/\/[^\/]+\/job\/([^\/]+))\/?([0-9]+)?\/?', url)
    #return jen_job(rev, reg.group(1) + ('/%d' % (int(reg.group(3)) + 1)),
    #               old_url if old_url else url)



def jen_rev(url, rev=None):
    """ Returns (job_name, job_url) for given revision. """

    from re import search

    try:
        url, rev = url
    except Exception:
        pass

    url = url.strip('/')
    url = search(r'^(https?:\/\/[^\/]+\/job\/([^\/]+))\/?([0-9]+)?\/?', url)
    build = url.group(3) if url.group(3) else '/lastBuild'
    job = jen_exe(url.group(1) + '/' + build)
    commits = []

    if job:
        commits = [
            item['revision'] for item in job['changeSet']['items'] if item]
        commits.sort()

    if rev in commits:
        return (url.group(2), url.group(1) + ('/%d' % job['number']))

    elif commits and rev > commits[-1]:
        return (url.group(2), url.group(1) + '/lastBuild') #('/%d' % (job['number'] + 1)))

    else:
        return jen_rev(url.group(1) + ('/%d' % (job['number'] - 1)), rev)


def jen_checker(jobs, users, queue, options):
    """ Process; checks for changes in Jenkins' jobs. """

    pool = Pool(processes=16)
    debug = options.debug

    while True:
        try:
            start = time()
            count = 0
            coun2 = 0
            tmp = {}

            for (rev, job, state, old) in [
                    j for j in pool.map(jen_job, [
                        (r, u) for (r, u) in jobs.keys()]) if j]:
                if old:
                    jobs[(rev, job)] = jobs[(rev, old)]
                    del jobs[(rev, old)]

                    if debug: # DEBUG ONLY
                        queue.append('JEN: [%s -> %s]' % (job, old))

                if jobs[(rev, job)]['state'] != state or old:

                    if debug and jobs[(rev, job)]['state'] != state: # DEBUG
                        queue.append('JEN: %s [%s -> %s](%d, %d)' % \
                            (job, jobs[(rev, job)]['state'], state,
                             rev, len(jobs[(rev, job)]['users'])))

                    for user in jobs[(rev, job)]['users']:

                        if user not in tmp:
                            tmp[user] = []

                        tmp[user].append({
                            'Revision': rev,
                            'Name':     jobs[(rev, job)]['name'],
                            'URL':      job,
                            'Status':   state
                        })

                    if state in [NONE, RUNNING]:
                        # be like proxy...
                        temp = jobs[(rev, job)]
                        temp['state'] = state
                        jobs[(rev, job)] = temp
                    else:
                        del jobs[(rev, job)]

                    if debug: # DEBUG ONLY
                        count += 1

                if debug: # DEBUG ONLY
                    coun2 += 1

            queue.extend([
                (users[user]['socket'], {'Jobs': {'Job': tmp[user]}})
                for user in tmp.keys() if user in users])

            if debug: # DEBUG ONLY
                queue.append('*jen: %f[s] (%d/%d/%d)' % \
                    (time() - start, count, coun2, len(jobs)))

            delta = time() - start
            sleep(30 - delta if delta < 30 else 0.1)

        except Exception, exc:
            if debug: # DEBUG ONLY
                queue.append(format_exc(exc))
