import re
from os.path import join

import bagit


def get_bag_info_fields(bag_path):
    """Returns """
    fields = {}
    patterns = ["(?P<key>[\\w\\-]+)", "(?P<val>.+)"]
    bag_info_path = join(bag_path, "bag-info.txt")
    try:
        with open(bag_info_path, "r") as f:
            for line in f.readlines():
                line = line.strip("\n")

                row_search = re.search(":?(\\s)?".join(patterns), line)
                if row_search:
                    key = row_search.group("key").replace("-", "_").strip()
                    val = row_search.group("val").strip()
                    if key in fields:
                        listval = [fields[key]]
                        listval.append(val)
                        fields[key] = listval
                    else:
                        fields[key] = val
    except FileNotFoundError:
        print(f"Could not find a bag-info.txt file at {bag_info_path}")
    return fields


def update_bag_info(bag_path, data):
    """Adds metadata from a dictionary to `bag-info.txt`"""
    assert isinstance(data, dict)
    bag = bagit.Bag(bag_path)
    for k, v in data.items():
        bag.info[k] = v
    bag.save()
