import datetime

long_wrapper_str = '##########################################'
medium_wrapper_str = '###############'


def plines(lst, WRAPPER=0, tab=0, pref='',line_after=False):

    if WRAPPER:
        if WRAPPER == 1:
            lst = [long_wrapper_str] + lst + [long_wrapper_str]
        elif WRAPPER == 2:
            lst = [medium_wrapper_str] + lst
        elif WRAPPER == 3:
            lst = lst + [medium_wrapper_str]

    for l in lst:
        if pref:
            l = "{} : {}".format(pref,l)
        print l if not tab else "{}{}".format('\t'*tab,l)
    if WRAPPER in [1,3]:
        print '\n'
    else:
        if line_after:
            print '\n'


def flines(lst, start=False,end=False,tab=2,pref='',line_after=False):

    if start:
        tab=1
        pref = 'func STR'
    elif end:
        tab=1
        pref = 'func END'

    plines(lst,tab=tab,pref=pref,line_after=line_after)


def cron_open(cron_code):
    plines(['{} cron start'.format(cron_code).upper(), datetime.datetime.now()], 1)


def cron_close(cron_code):
    plines(['{} cron end'.format(cron_code).upper(), datetime.datetime.now()], 1)


def spacer():
    print '\n'
