__author__ = 'klaudiagadek'
from argparse import ArgumentParser
import telnetlib

def get_scripts_options():
    parser = ArgumentParser(description='Tool to connect with RCP and turn on/off on Circuit',epilog="Example: wtipower --hostname=hostname --user=admin --password=1234 on 4")
    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument("--hostname", type=str, dest="hostname", required=True)
    requiredArguments.add_argument("--user", type=str, dest="username", required=True)  # Po co user
    requiredArguments.add_argument("--password", type=str, dest="password", required=True)
    requiredArguments.add_argument(type=str, dest="circuit_status", help="Circuit_status")
    requiredArguments.add_argument(dest="n", help="CKT name or number")
    args = parser.parse_args()
    return (args.hostname, args.username, args.password, args.circuit_status,args.n)

if __name__ == "__main__":
    (hostname,username,password,circuit_status, ckt_name_or_number)=get_scripts_options()
    print hostname, username,password,circuit_status,ckt_name_or_number
    telnet_session=telnetlib.Telnet(hostname,23,3)
    telnet_session.read_until("Enter Password:")
    telnet_session.write(password+ "\r\n")
    telnet_session.read_until(">")
    # Checking the status
    telnet_session.write("/S\r\n")
    output=telnet_session.read_until("RPC>")
    print output
    telnet_session.write("/SN\r\n")
    output2=telnet_session.read_until("RPC>")
    print output2

