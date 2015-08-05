__author__ = 'ute'
import urllib2
import re
'''
url = "http://infrastructure.emea.nsn-net.net/projects/btstools/lte_lmts/"
site_data = str(urllib2.urlopen(url).read())

site_data_matches = re.search('<a href="(.*)">R\d (LMTS latest build)<\/a>', site_data)
url_lates_build = site_data_matches.groups()[0]
print url_lates_build

site2_data = str(urllib2.urlopen(url_lates_build).read())
site2_data_matches = re.search('(Build artifacts .*)<br>*\s<a href="(.*)">',site2_data)
url_from_site2_data = site2_data_matches.groups()[1]
print url_from_site2_data
'''
url_from_site2_data = "http://lte.americas.nsn-net.net/scm/enb_official_builds/R18.0/LTE-LMTS/LTE-LMTS_R8.0_BLD-1.01.05"
url3 = re.search('(_R\d{1,3}.\d.*)', url_from_site2_data)
print url3.groups()[0]



