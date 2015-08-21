__author__ = 'kgadek'

import re
import yaml
import sys

#my_yaml_file


def create_row_files(yaml_file):
    raw_file=yaml_file.replace(".yml",".raw")
    raw_time_file=raw_file+".time"
    yaml_file=open(yaml_file,'r')
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

if __name__ == "__main__":
    yaml_file=sys.argv[1]
    create_row_files(yaml_file)
