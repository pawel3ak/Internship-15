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
    return (args.hostname, args.password, args.circuit_status, args.n)


def convert_circuit_status(circuit_status):
    if circuit_status == "on":
        return "/On"
    elif circuit_status == "off":
        return "/Off"
    else:
        print "Wrong circuit status"
        return ""


class Circuit_Turner():
    def __init__(self):
        self.telnet_session = ""

    def check_status(self):
        self.telnet_session.read_until(">")
        self.telnet_session.write("/S\r\n")
        circuit_status_options = self.telnet_session.read_until('-----+------------------+-------------+--------+-----------------+---------+')
        circuit_status_output = self.telnet_session.read_until('-----+------------------+-------------+--------+-----------------+---------+')
        print circuit_status_options, circuit_status_output

    def turn_on_or_off_circuit(self, circuit_status, ckt_name_or_number):
        self.telnet_session.read_until(">")
        self.telnet_session.write(circuit_status + " "+ckt_name_or_number + "\r\n")

    def set_telnet_session(self, hostname, password):
        self.telnet_session = telnetlib.Telnet(hostname, 23, 3)
        self.telnet_session.read_until("Enter Password:")
        self.telnet_session.write(password + "\r\n")

    def confirm_command(self):
        self.telnet_session.read_until("Sure? (Y/N):")
        self.telnet_session.write("Y\r\n")

    def close_telnet_session(self):
        self.telnet_session.read_until(">")
        self.telnet_session.close()
if __name__ == "__main__":
    (hostname, password, circuit_status, ckt_name_or_number) = get_scripts_options()
    circuit_status_command = convert_circuit_status(circuit_status)

    rcp_circuit_turner = Circuit_Turner()
    rcp_circuit_turner.set_telnet_session(hostname, password)
    rcp_circuit_turner.turn_on_or_off_circuit(circuit_status_command, ckt_name_or_number)
    rcp_circuit_turner.confirm_command()
    rcp_circuit_turner.check_status()
    rcp_circuit_turner.close_telnet_session()
