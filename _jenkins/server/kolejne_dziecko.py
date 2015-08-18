__author__ = 'ute'
def mmmm(parent_dict):
    print "kolejne dziecko widzi = ", parent_dict
    parent_dict['piec'] = 'szesc'
    from time import sleep
    sleep(2)
