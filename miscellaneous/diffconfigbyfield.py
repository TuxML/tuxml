"""``diffconfigbyfield`` is a simple utility that compares two
``.config`` files. Instead of showing a sorted output like the
``diffconfig`` of the Linux kernel (`source here
<https://github.com/torvalds/linux/blob/v4.14/scripts/diffconfig>`_),
``diffconfigbyfield`` shows the diff by field in the ``.config`` file.

Let's take the following extract of ``.config`` file:

    .. code-block::

      #
      # HID support
      #
      CONFIG_HID=y
      # CONFIG_HID_BATTERY_STRENGTH is not set
      CONFIG_HIDRAW=y
      CONFIG_UHID=m
      # CONFIG_HID_GENERIC is not set

* ``HID support`` is what we call **a field**; 
* from the line of ``CONFIG_HID``, ``HID`` is **a feature** or **an
  option** and ``y`` is its **value**.

**Output format:**
Added and removed items are shown with a leading plus or minus,
respectively. Changed items show the old and new values on a single
line with a leading ``~``.

**Output example:**

    .. code-block::
    
      * Default contiguous memory area size:
	   No changes
      * Bus devices
	  - MTD_BCM63XX_PARTS: m
	  ~ MTD_AR7_PARTS: m -> y
      * Partition parsers
	  + MTD_PARSER_TRX: y
      * User Modules And Translation Layers
	  ~ MTD_OOPS: m -> y
	  - MTD_PARTITIONED_MASTER: y
	  + SM_FTL: y

"""

USAGE =\
"""Usage:
\t$ diffconfigbyfield config1 config2
\twith config1 and config2 two configuration files (with .config format)
"""

__author__ = "Georges Aaron RANDRIANAINA"

import sys
import re


def read_config(config_file):
    """Read ``.config`` file and returns a dictionary representation of the
    ``.config`` file by field.

    For instance, with the ``.config`` example of the header comment,
    you'll get a dictionary like this: ``{"HID support": {"HID": "y",
    "HIDRAW": "y", "UHID": "m"}, ...}``
    
    It ignores features that are not set (for example
    ``CONFIG_HID_BATTERY_STRENGTH`` and ``CONFIG_HID_GENERIC`` here).

    :param config_file: path to a `.config` file
    :type config_file: string
    :return: a dictionary representation of the `.config` file.
    :rtype: dict

    """
    d = dict()
    category = "core"
    d[category] = dict()
    with open(config_file, 'r') as f:
        line = f.readline()
        while line:
            if line == "#\n":
                l = f.readline()
                if l == "# Automatically generated file; DO NOT EDIT.\n":
                    for _ in range(3):
                        f.readline()
                else:
                    category = l[2:-1]
                    if category not in d:
                        d[category] = dict()
                    f.readline()
            elif not line.startswith('#') and line != '\n':
                m = re.search(r'CONFIG_(\w+)=([\w"-/]+)', line)
                d[category][m.group(1)] = m.group(2)
            line = f.readline()
    return d


def compare_config_by_fields(config1, config2, verbose=False):
    """Compares two ``.config`` files and returns a dictionary that
    contains the diff:

    .. code-block:: python

      {field: {"added": {opt: value, ...},
               "changed": {opt: (old, new), ...},
               "removed": {opt: value}}, ...}

    with the ``.config`` example of header comment.

    :param config1: path to a ``.config`` file
    :type config1: str
    :param config2: path to another ``.config`` file
    :type config2: str
    :param verbose: set ``True`` iff you want to print the diff,\
    ``False`` otherwise. Default ``False``.
    :type verbose: bool
    :return: dictionary representation of the diff
    :rype: dict
    """
    cd1 = read_config(config1)
    cd2 = read_config(config2)
    res = dict()
    for field in cd1.keys():
        res[field] = dict()
        if field in cd2.keys():
            features1 = cd1[field]
            features2 = cd2[field]
            for f in features1:
                if f in features2:
                    v1 = features1[f]
                    v2 = features2[f]
                    if v1 != v2:
                        if "changed" not in res:
                            res[field]["changed"] = dict()
                        res[field]["changed"][f] = (v1, v2)
                else:
                    if "removed" not in res:
                        res[field]["removed"] = dict()
                    res[field]["removed"][f] = features1[f]
                    
            for f in features2:
                if f not in features1:
                    if "added" not in res:
                        res[field]["added"] = dict()
                    res[field]["added"][f] = features2[f]
    if verbose:
        for field in res:
            print("*", field)
            if not res[field]:
                print("\t No changes")
            for status in res[field]:
                for feat in res[field][status]:
                    getvalue = res[field][status]
                    if status == "added":
                        print("\t+ {}: {}".format(feat, getvalue[feat]))
                    elif status == "removed":
                        print("\t- {}: {}".format(feat, getvalue[feat]))
#                     changed
                    else:
                        v1, v2 = getvalue[feat]
                        print("\t~ {}: {} -> {}".format(feat, v1, v2))
    return res

def main():
    """Main function of the utility. Function that runs when using
    diffconfigbyfield with command line.
    """
    if len(sys.argv) != 3:
        print(USAGE)
        sys.exit()
    else:
        config1 = sys.argv[1]
        config2 = sys.argv[2]
        try:
            compare_config_by_fields(config1, config2, verbose=True)
        except FileNotFoundError as fnfe:
            print("File not found:", str(fnfe).split(':')[-1].strip())

if __name__ == "__main__":
    main()
