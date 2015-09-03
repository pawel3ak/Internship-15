__author__ = 'kgadek'
import re
import yaml
import sys
import os
from collections import OrderedDict

class OrderedDict(dict):  # my order
   def to_omap(self):
        return [('Nr', self['Nr']), ('Time', self['Time']),('Epoch', self['Epoch']),('Payload', self['Payload']),('Type_of_record', self['Type_of_record'])]


def represent_omap(dumper, data):  # zmienic
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.to_omap())


def to_ascii(buffer):
    output = re.sub(r'[^\x20-\x7e]',lambda matchobj: '<0x%s>' % ord(matchobj.group(0)),buffer)
    return output


def create_yml_files(filename_time,file_whole_payload):
    remaining_payload = file_whole_payload
    yaml.add_representer(OrderedDict, represent_omap)
    record_number=1
    line=filename_time.readline()
    filename_yaml=filename_raw.replace(".raw","")
    with open(filename_yaml+".yml", 'a') as new_yaml_file:
        while line:  # format of a line: 13:25:27.85 | 39 |> 1438601127.853814 |
            (timestamp, size, type_and_epoch,new_line_sign) = tuple(line.split("|"))
            size = int(size)
            type = type_and_epoch[0]
            epoch = type_and_epoch[2:]
            single_record_payload=remaining_payload[0:size]
            remaining_payload=remaining_payload[size:]
            single_record_payload=to_ascii(single_record_payload)
            log_data = OrderedDict({
                "Nr": record_number,
                "Time": timestamp,
                "Epoch": epoch,
                "Payload": single_record_payload,
                "Type_of_record":type})
            new_yaml_file.write( yaml.dump(log_data, default_flow_style=False, explicit_start=True) )
            record_number+=1
            line=filename_time.readline()


def get_and_convert_raw_files(raw_time_file,raw_file):
    time_file=open(str(raw_time_file),"r")
    log_file=open(str(raw_file),"r")
    rawfile_whole_payload=log_file.read()
    return (time_file, rawfile_whole_payload)


if __name__ == "__main__":
    #directory="/home/ute/ruff_scripts/log"
    directory="/home/ute/Logs_parser/logi"
    for filename in os.listdir(directory):
        if filename.endswith(".raw.time"):
            filename_time=os.path.join(directory, filename)
            filename_raw=filename_time.replace(".time","")
            (time_file, rawfile_whole_payload)=get_and_convert_raw_files(filename_time,filename_raw)
            create_yml_files(time_file,rawfile_whole_payload)
