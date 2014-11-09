#!/usr/bin/env python

import exifread
import getopt
import os
import re
import shutil
import sys

from dateutil.parser import parse

def make_destination_path(output_dir, date):
    return os.path.join(output_dir, str(date.year), str("%02d" % date.month), str("%02d" % date.day))

def ensure_destination_is_created(destination_dir):
    try:
        os.makedirs(destination_dir)
    except OSError, e:
        if e.errno != 17: # file exists
            raise OSError, e

def is_bad_date(date):
    p = re.compile(ur'\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}')
    if re.match(p, date):
        return True
    return False

def fix_date(date):
    return date[0:4] + '/' + date[5:7] + '/' + date[8:]

def copy_file(src, dst):
    print "copying %s to %s" % (src, dst)
    shutil.copy(src, dst)

def process(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            input_file = os.path.join(root, file)
            f = open(input_file, 'rb')
            tags = exifread.process_file(f)
            try:
                str_date = tags['Image DateTime'].printable
                if is_bad_date(str_date):
                    str_date = fix_date(str_date)
                date = parse(str_date)
            except KeyError:
                print "Not processing %s" % input_file
                destination_path = os.path.join(output_dir, 'MANUAL_PROCESSING')
            else:
                destination_path = make_destination_path(output_dir, date)
            ensure_destination_is_created(destination_path)
            copy_file(input_file, os.path.join(destination_path, file))

def usage(script_name):
    print "%s -i <input_dir> -o <output_dir>" % script_name

def main(argv):
    input_dir = ''
    output_dir = ''

    try:
        opts, args = getopt.getopt(argv[1:], "hi:o:", ["idir=", "odir="])
    except getopt.GetoptError:
        usage(argv[0])
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage(argv[0])
            sys.exit()
        elif opt in ("-i", "--idir"):
            input_dir = arg
        elif opt in ("-o", "--odir"):
            output_dir = arg

    if not os.path.isdir(input_dir):
        print "bad input dir %s" % input_dir
        sys.exit(2)

    if not os.path.isdir(output_dir):
        print "bad output dir %s" % output_dir
        sys.exit(2)


    process(input_dir, output_dir)

if __name__ == '__main__':
    main(sys.argv)
