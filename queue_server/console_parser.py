import re

def parser():
    with open('/home/ute/PycharmProjects/projekty/Internship-15/queue_server/test_output.txt') as console_input:
        console_input = console_input.read()
        match = (re.search('^(.*)\s*.\s[FAIL|PASS]', console_input))
        print match.groups()


if __name__ == '__main__':
    parser()
