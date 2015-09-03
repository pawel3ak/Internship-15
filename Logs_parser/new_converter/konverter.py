__author__ = 'ute'

import re
import yaml
import os
from argparse import ArgumentParser


def parser():
    parser = ArgumentParser(description='Make .raw and .row.time files.')
    parser.add_argument("--d", "-directory", type=str, help="Add directory", dest="directory", default="/home/ute/Logs_parser/logi")
    parser.add_argument("--y", "--YAML", help="Convert to yaml files", action="store_true", dest="is_yaml_conversion", default=True)
    parser.add_argument("--r", "--RAW", help="Convert to raw files", action="store_true", dest="is_raw_conversion", default=False)
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
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.to_omap())


def to_ascii(buffer):
    output = re.sub(r'[^\x21-\x7e]', lambda matchobj: '<0x%s>' % ord(matchobj.group(0)), buffer)
    return output


class OrderedDict(dict):  # my order
   def to_omap(self):
        return [('Nr', self['Nr']), ('Time', self['Time']), ('Epoch', self['Epoch']), ('Payload', self['Payload']),
                ('Type_of_record', self['Type_of_record'])]


class Converter(object):
    def __init__(self, directory):
        self.directory = directory
        self.filename_time = []
        self.filename_raw = []
        self.time_file = ""
        self.rawfile_whole_payload = ""
        self.filename_yml = []

    def find_raw_files(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".raw.time"):
                filename_time = os.path.join(self.directory, filename)
                filename_raw = filename_time.replace(".time", "")
                self.filename_time.append(filename_time)
                self.filename_raw.append(filename_raw)
        return len(self.filename_time)

    def create_yml_file(self, number_of_file):
        remaining_payload = self.rawfile_whole_payload
        yaml.add_representer(OrderedDict, represent_omap)
        record_number = 1
        line = self.time_file.readline()
        filename_yaml = self.filename_raw[number_of_file].replace(".raw", "")
        with open(filename_yaml+".yml", 'a') as new_yaml_file:
            while line:  # format of a line: 13:25:27.85 | 39 |> 1438601127.853814 |
                (timestamp, size, type_and_epoch, new_line_sign) = tuple(line.split("|"))
                size = int(size)
                type = type_and_epoch[0]
                epoch = type_and_epoch[2:]
                single_record_payload = remaining_payload[0:size]
                remaining_payload = remaining_payload[size:]
                single_record_payload = to_ascii(single_record_payload)
                log_data = OrderedDict({
                    "Nr": record_number,
                    "Time": timestamp,
                    "Epoch": epoch,
                    "Payload": single_record_payload,
                    "Type_of_record": type})
                new_yaml_file.write(yaml.dump(log_data, default_flow_style=False, explicit_start=True))
                record_number += 1
                line = self.time_file.readline()

    def find_yml_files(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".yml"):
                filename_yml = os.path.join(self.directory, filename)
                self.filename_yml.append(filename_yml)
        return len(self.filename_yml)

    def get_and_convert_raw_file(self, number_of_file):
        self.time_file = open(str(self.filename_time[number_of_file]), "r")
        log_file = open(str(self.filename_raw[number_of_file]), "r")
        self.rawfile_whole_payload = log_file.read()

    def create_raw_file(self, number_of_file):
        filename_raw = self.filename_yml[number_of_file].replace(".yml", ".raw")
        filename_raw_time = filename_raw+".time"
        with open(self.filename_yml[number_of_file], 'r') as filename_yaml:
            yaml_data = yaml.load_all(filename_yaml)
        for filename in os.listdir(self.directory):
            filename = os.path.join(self.directory, filename)
            if filename == filename_raw:
                os.rename(filename, filename+'.bak')
            elif filename == filename_raw_time:
                os.rename(filename, filename+'.bak')
        with open(filename_raw, 'w') as raw_file, open(filename_raw_time, 'w') as raw_time_file:
            for record in yaml_data:
                record_timestamp = ""
                record_size = 0
                record_type = ""
                record_epoch = ""
                record_payload = ""
                for key, value in record.items():
                    if key == "Time":
                        record_timestamp = value
                    elif key == "Type_of_record":
                        record_type = value
                    elif key == "Epoch":
                        record_epoch = value
                    elif key == "Payload":
                        record_payload = ascii_to_dec(value)
                        record_size = len(record_payload)
                rawtime_record_line = "%s| %7.7s |%s %s|\n" % (record_timestamp, record_size, record_type, record_epoch)
                raw_file.write(record_payload)
                raw_time_file.write(rawtime_record_line)


if __name__ == "__main__":
    (directory, is_yaml_conversion) = parser()
    file_converter = Converter(directory)
    if is_yaml_conversion:
        number_of_files = file_converter.find_raw_files()
        for number_of_file in range(0, number_of_files):
            file_converter.get_and_convert_raw_file(number_of_file)
            file_converter.create_yml_file(number_of_file)
    else:
        number_of_files = file_converter.find_yml_files()
        for number_of_file in range(0, number_of_files):
            file_converter.create_raw_file(number_of_file)
