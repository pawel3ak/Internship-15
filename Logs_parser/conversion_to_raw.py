__author__ = 'kgadek'
import re
import yaml
import sys
import os

def ascii_to_dec(buffer):
    output = re.sub(r"<0x(..)>",lambda matchobj: chr(int(matchobj.group(1))),buffer)
    return output


def create_raw_files(filename_yaml, directory):
    filename_raw=filename_yaml.replace(".yml",".raw")
    filename_raw_time=filename_raw+".time"
    filename_yaml=open(directory+"/"+filename_yaml,'r')
    yaml_data=yaml.load_all(filename_yaml)
    filename_raw = os.path.join(directory, filename_raw)
    filename_raw_time = os.path.join(directory, filename_raw_time)
    for filename in os.listdir(directory):
        filename = os.path.join(directory, filename)
        if filename==filename_raw:
            print filename_raw
            os.rename(filename, filename+'.bak')
        elif filename==filename_raw_time:
            print filename_raw_time
            os.rename(filename, filename+'.bak')
    with open(filename_raw,'w') as raw_file, open(filename_raw_time,'w') as raw_time_file:
        for record in yaml_data:
            for key,value in record.items():
                if key=="Time":
                    record_timestamp=value
                elif key=="Type_of_record":
                    record_type=value
                elif key=="Epoch":
                    record_epoch=value
                elif key=="Payload":
                    record_payload=ascii_to_dec(value)
                    record_size = len(record_payload)
            rawtime_record_line = "%s | %7.7s |%s %s |\n" % (record_timestamp, record_size, record_type, record_epoch)
            raw_file.write(record_payload)
            raw_time_file.write(rawtime_record_line)


if __name__ == "__main__":
    #directory="/home/ute/ruff_scripts/log"
    directory="/home/ute/Logs_parser/logi"
    for filename in os.listdir(directory):
        if filename.endswith(".yml"):
            create_raw_files(filename,directory)
