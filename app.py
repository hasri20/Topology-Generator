from textfsm import TextFSM
from netmiko import ConnectHandler
from inquirer import prompt, Text, Password
from networkx import draw, Graph
from matplotlib.pyplot import show

while True:
    questions = [
        Text(name='ip_file', message="Input your ip file list"),
    ]

    answers = prompt(questions)

    try:
        ip_file = open(answers['ip_file'], 'r').readlines()
    except FileNotFoundError:
        print("Wrong file or file path")
    else:
        break

account = [
    Text(name='username', message="Input your username"),
    Password(name='password', message="Input your password")
]

credential = prompt(account)

list_ip = [line.strip() for line in ip_file]

graph = Graph()

for ip in list_ip:

    print("connecting to router at " + ip)
    cisco_vios = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': credential['username'],
        'password': credential['password'],
    }

    net_connect = ConnectHandler(**cisco_vios)
    neighbors = net_connect.send_command(
        "show cdp neighbors detail | include Device").replace("Device ID: ", "")

    neighbors_raw = neighbors.split('\n')

    running_configuration = net_connect.send_command("show run")

    template_file = open("show_run.template")
    template = TextFSM(template_file)
    result = template.ParseText(running_configuration)
    for item in result:
        hostname = ('.'.join(item))

    for item in neighbors_raw:
        graph.add_edge(hostname, item)


draw(graph, with_labels=True)
show()
