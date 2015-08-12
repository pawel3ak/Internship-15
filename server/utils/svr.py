"""
doc string...
"""
from traceback import format_exc

from utils.xlm import xml2dict
from utils.jen import jen_exe
from utils.svn import svn_log


def svr_request(ipport, fileno, request, queue,
                users, repos, jenks, jobs, options):
    """ doc string... """

    debug = options.debug

    try:
        for user in [x for x in users.keys() if x != ipport and \
                                                users[x]['socket'] == fileno]:
            # before new config, close old connection to given socket
            svr_disconnect(user, queue, users, repos, jobs, options)

        try:
            request = xml2dict(
                request.replace('encoding="utf-16"', ''))['DataToSend']
            request['Logins']['Login'] and request['Repos']['Repository']
        except:
            queue.append(
                (fileno, {'Messages': {'Message' : '400 Bad Request'}}))
            return

        errors = []
        tmp = {}

        if not isinstance(request['Repos']['Repository'], list):
            request['Repos']['Repository'] = [request['Repos']['Repository']]

        for repo in request['Repos']['Repository']:
            try:
                tmp[(repo['Url'], repo['Jenkins'] if repo['Jenkins'] else '')] \
                    = svn_log(
                        repo['Url'], ['-l', '1'], repo['Login'],
                        repo['Pass'])[0]['rev']
            except:
                errors.append(
                    "'%s' - connection failure. Check your configuration." % \
                        repo['Url'])

            if repo['Jenkins'] and not jen_exe(repo['Jenkins']):
                errors.append(
                    "Invalid Jenkins URL: '%s'. Check your configuration." % \
                        repo['Jenkins'])

        if errors:
            queue.append((fileno, {'Messages': {'Message': errors}}))
            return

        queue.append((fileno, {'Messages': {'Message': 'HELLO'}}))

        old = users[ipport] if ipport in users else None

        users[ipport] = {
            'socket': fileno,
            'repos': [(x['Url'], x['Jenkins'] if x['Jenkins'] else '') \
                for x in request['Repos']['Repository']],
            'users': [x for x in request['Logins']['Login']]
        }

        for repo in request['Repos']['Repository']:
            if not repo['Jenkins']:
                repo['Jenkins'] = ''

            if (repo['Url'], repo['Jenkins']) in repos:
                # add client to repository followers
                if ipport not in repos[(repo['Url'], repo['Jenkins'])]['users']:
                    temp = repos[(repo['Url'], repo['Jenkins'])]
                    temp['users'].append(ipport)
                    repos[(repo['Url'], repo['Jenkins'])] = temp

            else:
                # add repository to list of monitored ones
                repos[(repo['Url'], repo['Jenkins'])] = {
                    'username': repo['Login'] if repo['Login'] else None,
                    'password': repo['Pass'] if repo['Pass'] else None,
                    'revision': tmp[(repo['Url'], repo['Jenkins'])],
                    'users': [ipport]
                }
                queue.append('repos += %s@(%s, %s)' % (
                    repo['Login'], repo['Url'], repo['Jenkins']))

            if repo['Jenkins']:
                # (re)load jobs list for given Jenkins URL
                j = {}
                for (name, url) in [(x['name'], x['url']) for x in \
                        jen_exe(repo['Jenkins'])['jobs'] \
                        if x['color'] != 'disabled']:
                    j[name] = url
                jenks[repo['Jenkins']] = j

        if old:
            for repo in old['repos']:
                if repo not in users[ipport]['repos']:
                    temp = repos[repo]
                    temp['users'].remove(ipport)

                    if len(temp['users']) == 0:
                        del repos[repo]
                    else:
                        repos[repo] = temp

        if debug: # DEBUG ONLY
            if old:
                queue.append('users ~= %s' % str(ipport))
            else:
                queue.append('users += %s' % str(ipport))

    except Exception, exc:
        if debug: # DEBUG ONLY
            queue.append(format_exc(exc))


def svr_disconnect(fileno, queue, users, repos, jobs, options):
    """ doc string... """
    debug = options.debug

    try:
        user = None

        if isinstance(fileno, (tuple, list)):
            user = fileno
        elif isinstance(fileno, int):
            user = [x for x in users.keys() if users[x]['socket'] == fileno]
            if user:
                user = user[0]

        if user:
            # clear repos list
            for repo in users[user]['repos']:
                try:
                    if user in repos[repo]['users']:
                        tmp = repos[repo]
                        tmp['users'].remove(user)

                        if len(tmp['users']) == 0:
                            del repos[repo]
                        else:
                            repos[repo] = tmp

                except Exception, exc:
                    if debug: # DEBUG ONLY
                        queue.append(format_exc(exc))

            # clear jobs list
            for url in jobs.keys():
                try:
                    if user in jobs[url]['users']:
                        tmp = jobs[url]
                        tmp['users'].remove(user)

                        if (len(tmp['users']) == 0 or
                                tmp['state'] not in ['NONE', 'RUNNING']):
                            del jobs[url]
                        else:
                            jobs[url] = tmp

                except Exception, exc:
                    if debug: # DEBUG ONLY
                        queue.append(format_exc(exc))

            # finally, delete user from list
            del users[user]

            if debug: # DEBUG ONLY
                queue.append('users -= %s' % str(user))

    except Exception, exc:
        if debug: # DEBUG ONLY
            queue.append(format_exc(exc))
