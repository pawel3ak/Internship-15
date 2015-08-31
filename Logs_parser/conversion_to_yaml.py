__author__ = 'kgadek'
import re
import yaml
import sys

#files names


#yaml class not to set alphabetic dict
class MyDict(dict):
   def to_omap(self):
        return [('Nr', self['Nr']), ('Time', self['Time']),('Epoch', self['Epoch']),('Payload', self['Payload']),('Type_of_record', self['Type_of_record'])]

def represent_omap(dumper, data):
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.to_omap())

def create_yml_files(f1,logs,num_lines):
    yaml.add_representer(MyDict, represent_omap)
    count=1
    for i in range (0,num_lines):
        line=f1.readline()
        splited=line.split("|")
        time_socket=splited[0]
        size=int(splited[1])
        type_of__record=splited[2][0]
        time_epoch=splited[2][2:]
        log=logs[0:size]
        logs=logs[size:]
        log=log.replace("\n","<\\n>")
        data = MyDict({
            "Nr": count,
            "Time": time_socket,
            "Epoch": time_epoch,
            "Payload": log,
            "Type_of_record":type_of__record})
        yaml_file=raw_file.replace(".raw","")
        with open(yaml_file+".yml", 'a') as outfile:
            outfile.write( yaml.dump(data, default_flow_style=False, explicit_start=True) )
        count+=1
        outfile.close()

def get_raw_files(raw_time_file,raw_file):
    f1=open(str(raw_time_file),"r")
    f2=open(str(raw_file),"r")
    num_lines = sum(1 for line in f1)
    f1.seek(0)
    logs=f2.read()
    create_yml_files(f1,logs,num_lines)
    #to yaml file


if __name__ == "__main__":
    raw_time_file=sys.argv[1]
    raw_file=sys.argv[2]
    get_raw_files(raw_time_file,raw_file)


