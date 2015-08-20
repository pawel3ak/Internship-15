__author__ = 'kgadek'
import re
import yaml

count=1
raw_time_file="_json_rpc_tests--127.0.0.1.34255.raw.time"
raw_file="_json_rpc_tests--127.0.0.1.34255.raw"
f1=open(str(raw_time_file),"r")
f2=open(str(raw_file),"r")
num_lines = sum(1 for line in f1)
f1.seek(0)
logs=f2.read()

#dict
class MyDict(dict):
   def to_omap(self):
      return [('Nr', self['Nr']), ('Time', self['Time']),('Epoch', self['Epoch']),('Payload', self['Payload']),('Type_of_record', self['Type_of_record'])]

def represent_omap(dumper, data):
   return dumper.represent_mapping(u'tag:yaml.org,2002:map', data.to_omap())
yaml.add_representer(MyDict, represent_omap)
#to yaml file
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

    with open('data.yml', 'a') as outfile:
        outfile.write( yaml.dump(data, default_flow_style=False, explicit_start=True) )
    count+=1
    outfile.close()

#from yaml file
yaml_file=open('data.yml','r')
yaml_data=yaml.load_all(yaml_file)
new_raw_time_file=open("new"+raw_time_file,'w')
new_raw_file=open("new"+raw_file,'w')
for record in yaml_data:
    for key,value in record.items():
        if str(key)=="Time":
            new_time_socket=value
        if str(key)=="Type_of_record":
            new_type_of_record=value
        if str(key)=="Epoch":
            new_time_epoch=value
        if str(key)=="Payload":
            value=re.sub(r'\<\\n\>', "\n", value)
            new_size=str(len(value))
            new_size_len=len(new_size)
            for i in range(0,7-new_size_len):
                new_size=" "+new_size

    new_raw_time_file.write(str(new_time_socket)+"|"+str(new_size)+" |"+str(new_type_of_record)+" "+str(new_time_epoch)+"|\n")
    new_raw_file.write(value)
new_raw_time_file.close()
