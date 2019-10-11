def file_size(num):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0


def label_class(status):
    label_class = 'green'
    if status in [10, 20]:
        label_class = 'yellow'
    elif status in [30, 60]:
        label_class = 'red'
    return label_class
