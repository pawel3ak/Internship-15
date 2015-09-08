__author__ = 'klaudiagadek'
from argparse import ArgumentParser
import telnetlib


def get_scripts_options():
    parser = ArgumentParser(description='Tool to connect with RCP and turn on/off Circuit',
                            epilog="Example: wtipower --hostname=hostname --user=admin --password=1234 on 4")
    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument("--hostname", type=str, dest="hostname", required=True)
    parser.add_argument("--user", type=str, dest="username", default="admin")
    requiredArguments.add_argument("--password", type=str, dest="password", required=True)
    requiredArguments.add_argument(type=str, dest="circuit_status", help='<on/off>')
    requiredArguments.add_argument(dest="n", help='required CKT name or number')
    args = parser.parse_args()
    return (args.hostname, args.username, args.password, args.circuit_status, args.n)


def check_status(telnet_session):
    #telnet_session.read_until(">")
    #gotelnet_session.write("/S\r\n")
    circuit_status_options = telnet_session.read_until('-----+------------------+-------------+--------+-----------------+---------+')
    circuit_status_output = telnet_session.read_until('-----+------------------+-------------+--------+-----------------+---------+')
    print circuit_status_options, circuit_status_output


def convert_circuit_status(circuit_status):
    if circuit_status == "on":
        return "/On"
    elif circuit_status == "off":
        return "/Off"
    else:
        print "Wrong circuit status"
        return ""


def turn_on_off_circuit(telnet_session, circuit_status, ckt_name_or_number):
    telnet_session.read_until(">")
    telnet_session.write(circuit_status + " "+ckt_name_or_number + "\r\n")

def confirm_command():
    telnet_session.read_until("Sure? (Y/N):")
    telnet_session.write("Y\r\n")

def set_telnet_session(hostname, password):
    telnet_session = telnetlib.Telnet(hostname, 23, 3)
    telnet_session.read_until("Enter Password:")
    telnet_session.write(password + "\r\n")
    return telnet_session


if __name__ == "__main__":
    (hostname, username, password, circuit_status, ckt_name_or_number) = get_scripts_options()
    circuit_status_command = convert_circuit_status(circuit_status)

    telnet_session = set_telnet_session(hostname, password)
    turn_on_off_circuit(telnet_session, circuit_status_command, ckt_name_or_number)
    confirm_command()
    check_status(telnet_session)
    telnet_session.read_until(">")
    telnet_session.close()
