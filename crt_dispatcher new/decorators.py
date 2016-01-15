from warnings import simplefilter
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

__author__ = 'Pawel Tarsa'
__copyright__ = 'Copyright 2015, Nokia'
__version__ = '2015-12-11'
__maintainer__ = 'Pawel Tarsa'
__email__ = 'pawel.tarsa@nokia.com'


def suppress_insecure_platform_warnings(function):
    def wrapped(*args, **kwargs):
        simplefilter(action='ignore', category=InsecurePlatformWarning)
        return function(*args, **kwargs)

    return wrapped
