__author__ = 'klaudia_gadek'

import re
import yaml
import os
from argparse import ArgumentParser


def get_scripts_options():
    parser = ArgumentParser(description='Tool to convert betwen TAF raw log and TAF yaml log formats')
    parser.add_argument("--d", "--logs_location", type=str, help="Add directory", dest="directory", default="/home/ute/Logs_parser")
    parser.add_argument("--y", "--to_yaml", help="Convert to yaml files", action="store_true", dest="is_yaml_conversion", default=True)
    parser.add_argument("--r", "--to_raw", help="Convert to raw files", action="store_true", dest="is_raw_conversion", default=False)
    args = parser.parse_args()
    if args.directory != None:
        print "\tMy directory: "+args.directory
    if args.is_raw_conversion:
        print "\tType of conversion: RAW"
        args.is_yaml_conversion = False
    if args.is_yaml_conversion:
        print "\tType of conversion: YAML"
    return (args.directory,args.is_yaml_conversion)


def ascii_to_dec(buffer):
    output = re.sub(r"<0x(..)>", lambda matchobj: chr(int(matchobj.group(1))), buffer)
    return output


def represent_omap(dumper, data):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.get_log_record_items())


def to_ascii(buffer):
    output = re.sub(r'[^\x21-\x7e]', lambda matchobj: '<0x%s>' % ord(matchobj.group(0)), buffer)
    return output


class LogsRecord(dict):
   def get_log_record_items(self):
        return [('Nr', self['Nr']), ('Time', self['Time']), ('Epoch', self['Epoch']), ('Payload', self['Payload']),
                ('Type_of_record', self['Type_of_record'])]


class TafLogsConverter(object):
    def __init__(self, directory):
        self.directory = directory
        self.filename_raw = []
        self.time_file = ""
        self.rawfile_whole_payload = ""
        self.filename_yml = []

    def find_raw_files(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".raw"):
                filename_raw = os.path.join(self.directory, filename)
                self.filename_raw.append(filename_raw)

    def create_yml_file(self, raw_filename):
        remaining_payload = self.rawfile_whole_payload
        yaml.add_representer(LogsRecord, represent_omap)
        record_number = 1
        filename_yaml = (raw_filename.replace(".raw", ""))+".yml"
        self.backup_conversion_target_files(filename_yaml)
        with open(filename_yaml, 'a') as new_yaml_file:
            while True:  # format of a line: 13:25:27.85 | 39 |> 1438601127.853814 |
                line = self.time_file.readline()
                if not line:
                    break
                (timestamp, size, type_and_epoch, _) = tuple(line.split("|"))
                log_data = LogsRecord({
                    "Nr": record_number,
                    "Time": timestamp,
                    "Epoch": type_and_epoch[2:],
                    "Payload": to_ascii(remaining_payload[0:int(size)]),
                    "Type_of_record": type_and_epoch[0]})
                remaining_payload = remaining_payload[int(size):]
                new_yaml_file.write(yaml.dump(log_data, default_flow_style=False, explicit_start=True))
                record_number += 1

    def find_yml_files(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".yml"):
                filename_yml = os.path.join(self.directory, filename)
                self.filename_yml.append(filename_yml)

    def get_and_convert_raw_file(self, raw_filename):
        self.time_file = open(raw_filename+".time", "r")
        log_file = open(raw_filename, "r")
        self.rawfile_whole_payload = log_file.read()

    def create_raw_file(self, yaml_filename):
        filename_raw = yaml_filename.replace(".yml", ".raw")
        filename_raw_time = filename_raw+".time"
        with open(yaml_filename, 'r') as filename_yaml:
            yaml_data = yaml.load_all(filename_yaml)
            self.backup_conversion_target_files(filename_raw)
            self.backup_conversion_target_files(filename_raw_time)
            with open(filename_raw, 'w') as raw_file, open(filename_raw_time, 'w') as raw_time_file:
                for record in yaml_data:
                    record_payload = ascii_to_dec(record['Payload'])
                    record_size = len(record_payload)
                    rawtime_record_line = "%s| %7.7s |%s %s|\n" % (record['Time'], record_size, record['Type_of_record'], record['Epoch'])
                    raw_file.write(record_payload)
                    raw_time_file.write(rawtime_record_line)

    def get_number_of_files(self, is_yaml_conversion):
        if is_yaml_conversion:
            return len(self.filename_raw)
        else:
            return len(self.filename_yml)

    def get_filename(self,is_yaml_conversion,number_of_file):
        if is_yaml_conversion:
            return self.filename_raw[number_of_file]
        else:
            return self.filename_yml[number_of_file]
    def backup_conversion_target_files(self,filename_to_check):
        for filename in os.listdir(self.directory):
                filename = os.path.join(self.directory, filename)
                if filename == filename_to_check:
                    os.rename(filename, filename+'.bak')

    def convert_to_yaml_format(self, is_yaml_conversion):
        number_of_files = file_converter.get_number_of_files(is_yaml_conversion)
        for number_of_file in range(0, number_of_files):
            raw_filename = file_converter.get_filename(is_yaml_conversion, number_of_file)
            file_converter.get_and_convert_raw_file(raw_filename)
            file_converter.create_yml_file(raw_filename)

    def convert_to_raw_format(self, is_yaml_conversion):
        number_of_files = file_converter.get_number_of_files(is_yaml_conversion)
        for number_of_file in range(0, number_of_files):
            yaml_filename = file_converter.get_filename(is_yaml_conversion, number_of_file)
            file_converter.create_raw_file(yaml_filename)


if __name__ == "__main__":
    (directory, is_yaml_conversion) = get_scripts_options()
    file_converter = TafLogsConverter(directory)
    if is_yaml_conversion:
        file_converter.find_raw_files()
        file_converter.convert_to_yaml_format(is_yaml_conversion)
    else:
        file_converter.find_yml_files()
        file_converter.convert_to_raw_format(is_yaml_conversion)
