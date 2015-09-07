__author__ = 'klaudia_gadek'

import re
import yaml
import os
from argparse import ArgumentParser


def get_scripts_options():
    parser = ArgumentParser(description='Tool to convert between TAF raw log and TAF yaml log formats')
    parser.add_argument("--l", "--logs_location", type=str, help="Directory with logs to convert", dest="logs_location", default="/home/ute/ruff_startup/logs/play")
    parser.add_argument("--2y", "--to_yaml", help="Convert to yaml files", action="store_true", dest="is_conversion_to_yaml", default=True)
    parser.add_argument("--2r", "--to_raw", help="Convert to raw files", action="store_true", dest="is_conversion_to_raw", default=False)
    args = parser.parse_args()
    if args.logs_location != None:
        print "\tWill convert logs from: "+args.logs_location
    if args.is_conversion_to_raw:
        print "\tWill convert to raw format"
        args.is_conversion_to_yaml = False
    elif args.is_conversion_to_yaml:
        print "\tWill convert to yaml format"
    return (args.logs_location, args.is_conversion_to_yaml)


def restore_non_printable(buffer):
    output = re.sub(r"<0x(..)>", lambda matchobj: chr(int(matchobj.group(1),16)), buffer)
    return output


def non_printable_to_ascii(buffer):
    output = re.sub(r'[^\x21-\x7e]', lambda matchobj: '<0x%2.2x>' % ord(matchobj.group(0)), buffer)
    return output


def represent_omap(dumper, data):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.get_log_record_items())


class LogsRecord(dict):
   def get_log_record_items(self):
        return [('Nr', self['Nr']), ('Time', self['Time']), ('Epoch', self['Epoch']), ('Payload', self['Payload']),
                ('Type_of_record', self['Type_of_record'])]


class TafLogsConverter(object):
    def __init__(self, logs_location):
        self.logs_location = logs_location

    def create_yaml_file(self, filename):
        raw_filename=filename+".raw"
        raw_time_filename=raw_filename+".time"
        filename_yaml = filename+".yml"
        self.backup_conversion_target_files(filename_yaml)

        with open(filename_yaml, 'a') as new_yaml_file, \
             open(raw_time_filename) as raw_time_file, \
             open(raw_filename) as raw_file:
            self._create_yaml_file(new_yaml_file,raw_time_file,raw_file)


    def _create_yaml_file(self, new_yaml_file,raw_time_file,raw_file):
        yaml.add_representer(LogsRecord, represent_omap)
        record_number = 1
        # format of a line: 13:25:27.85 | 39 |> 1438601127.853814 |
        for line in raw_time_file:
            (timestamp, size, type_and_epoch, _) = tuple(line.split("|"))
            payload=raw_file.read(int(size))
            log_data = LogsRecord({
                "Nr": record_number,
                "Time": timestamp,
                "Epoch": type_and_epoch[2:],
                "Payload": non_printable_to_ascii(payload),
                "Type_of_record": type_and_epoch[0]})
            new_yaml_file.write(yaml.dump(log_data, default_flow_style=False, explicit_start=True))
            record_number += 1

    def create_raw_file(self, filename):
        filename_raw = filename+".raw"
        filename_raw_time = filename_raw+".time"
        yaml_filename=filename+".yml"
        self.backup_conversion_target_files(filename_raw)
        self.backup_conversion_target_files(filename_raw_time)

        with open(yaml_filename, 'r') as filename_yaml,\
             open(filename_raw, 'w') as raw_file, \
             open(filename_raw_time, 'w') as raw_time_file:
            self._create_raw_file(filename_yaml,raw_file,raw_time_file)

    def _create_raw_file(self, filename_yaml,raw_file,raw_time_file):
        yaml_data = yaml.load_all(filename_yaml)
        for record in yaml_data:
            record_payload = restore_non_printable(record['Payload'])
            record_size = len(record_payload)
            rawtime_record_line = "%s|%7.7s |%s %s|\n" % (record['Time'], record_size, record['Type_of_record'], record['Epoch'])
            raw_file.write(record_payload)
            raw_time_file.write(rawtime_record_line)

    def backup_conversion_target_files(self, filename_to_check):
        for filename in os.listdir(self.logs_location):
                filename = os.path.join(self.logs_location, filename)
                if filename == filename_to_check:
                    os.rename(filename, filename+'.bak')

    def convert_to_yaml_format(self):
        for filename in os.listdir(self.logs_location):
            if filename.endswith(".raw"):
                raw_filename = os.path.join(self.logs_location, filename)
                filename=raw_filename.replace(".raw","")
                self.create_yaml_file(filename)

    def convert_to_raw_format(self):
        for filename in os.listdir(self.logs_location):
            if filename.endswith(".yml"):
                yaml_filename = os.path.join(self.logs_location, filename)
                filename=yaml_filename.replace(".yml","")
                self.create_raw_file(filename)


if __name__ == "__main__":
    (logs_location, is_conversion_to_yaml) = get_scripts_options()
    file_converter = TafLogsConverter(logs_location)
    if is_conversion_to_yaml:
        file_converter.convert_to_yaml_format()
    else:
        file_converter.convert_to_raw_format()
