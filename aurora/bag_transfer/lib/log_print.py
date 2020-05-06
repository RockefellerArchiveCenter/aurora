import datetime

long_wrapper_str = "##########################################"
medium_wrapper_str = "###############"


def plines(lst, WRAPPER=0, tab=0, pref="", line_after=False):

    if WRAPPER:
        if WRAPPER == 1:
            lst = [long_wrapper_str] + lst + [long_wrapper_str]
        elif WRAPPER == 2:
            lst = [medium_wrapper_str] + lst
        elif WRAPPER == 3:
            lst = lst + [medium_wrapper_str]

    for line in lst:
        if pref:
            line = "{} : {}".format(pref, line)
        print(line if not tab else "{}{}".format("\t" * tab, line))
    if WRAPPER in [1, 3]:
        print("\n")
    else:
        if line_after:
            print("\n")


def cron_open(cron_code):
    plines(["{} cron start".format(cron_code).upper(), datetime.datetime.now()], 1)


def cron_close(cron_code):
    plines(["{} cron end".format(cron_code).upper(), datetime.datetime.now()], 1)


def spacer():
    print("\n")
