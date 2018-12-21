from prettytable import PrettyTable
import csv, os, sys
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from fabric import Connection
import configparser
from glob import glob

def directory():
    config = configparser.ConfigParser()
    config.read("toolkit.conf")
    return config.get('toolkit', 'path')

def readerCSV(project):
    if project is None:
        print('Order not found')
        sys.exit()
    with open(directory()+'{project}/docs/credentials.csv'.format(project=project), mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        lines = 0
        for row in csv_reader:
            if lines is 0:
                keys = row
                lines += 1
            else:
                values = row
        dictionary = dict(zip(keys, values))
        return dictionary

def show(project):
    info = readerCSV(project)
    t = PrettyTable(['Key', 'Value'])
    t.add_row(['Name', project])
    t.add_row(['Provider', 'AWS'])
    for k, v in info.items():
        t.add_row([k,v])
    return t

def console(project):
    info = readerCSV(project)
    if not 'Console login link' in info:
        print('This project has not cloud infrastructure')
        sys.exit()
    browser = webdriver.Firefox()
    browser.get(info['Console login link'])
    username = browser.find_element_by_id('username')
    username.send_keys(info['User name'])
    password = browser.find_element_by_id('password')
    password.send_keys(info['Password'])
    browser.find_element_by_id('signin_button').click()
    return ""

def github(project):
    info = readerCSV(project)
    os.system("firefox --new-window '{url}'".format(url=info['Github']))
    return ''

def ssh(project, name):
    info = readerCSV(project)
    if name is None or not 'ssh '+name in info:
        print('This project has not a ec2 attached')
        sys.exit()
    host = info['ssh '+name]
    user = "ubuntu"
    key_filename = '{directory}{project}/docs/pem/{pem}.pem'.format(directory=directory(), project=project, pem=name)
    c = Connection(host=host, user=user, connect_kwargs={"key_filename": key_filename})
    result = c.run('ls -al')
    return result

def actions():
    print("List of action:")    
    print("show [project]            - Show projects details ")
    print("console [project]         - Open provider console")
    print("github [project]          - Open github repo of the project")
    print("ssh [project]             - Ssh to the ec2")
    print("actions                   - List of available actions")
    print("create [project]          - Create new projects")
    print("import [project] [name]   - Import Angular component")
    print("goalous                   - Open goalous web page")
    print("projects                  - List of available projects")
    return ""

def projects():
    print("List of projects:")
    for path in glob(directory()+"*/"):
        print("- {path}".format(path=path.split('/')[-2]))
    return ''

def create(project):
    title = 'Choose framework: '
    frameworks = ['Angular', 'Simple page', 'RoR', 'Django', 'Laravel']
    framework, index = pick(frameworks, title)

    title = 'Choose infrastructure (press SPACE to mark, ENTER to continue):'
    if index in (0,1):
        options = ['S3', 'CloudFront', 'Lambda', "Travis CI", "Route 53"]
    elif index in (2,3,4,5):
        options = ['Docker', 'S3', 'CloudFront', 'Lambda', 'EC2', 'Nginx', "CI", "Route 53"]
    selected = pick(options, title, multi_select=True, min_selection_count=1)

    for i in selected:
        print("- {option}".format(option=i[0]))

    # try:
    #     if not os.path.exists(directory+'{action}/docs'.format(action=action)):
    #         os.makedirs(directory+'{action}/docs'.format(action=action))
    #         os.makedirs(directory+'{action}/deploy'.format(action=action))
    #         os.makedirs(directory+'{action}/src'.format(action=action))
    #         return "Project created successfully!"
    # except OSError:
    #     return 'Error: Creating directory. '+action
    # info = readerCSV()
    # aws.createS3(info, action)
    # print("S3 bucket '{action}' was successfully created!".format(action))


def importer(project, component):
    atomic = component.split('/')[2]
   
    dir_src = ('~/projects/isao/library/src/app/{component}/'.format(component=component))
    dir_dst = ('~/testing/{project}/src/src/app/{project}/{atomic}/'.format(project=project, atomic=atomic))

    if not os.path.exists("{dir_dst}/{name}".format(dir_dst=dir_dst, name=component.split('/')[-1])):
        os.mkdir("{dir_dst}/{name}".format(dir_dst=dir_dst, name=component.split('/')[-1]))

    for filename in os.listdir(dir_src):
        shutil.copy( dir_src + filename, "{dir_dst}/{name}".format(dir_dst=dir_dst, name=component.split('/')[-1]))
        print("COPY - "+filename)

    filename = "~/testing/{project}/src/src/app/app.module.ts".format(project=project)
    path = "/".join(component.split("/")[2:])
    name = "{ "+component.split("/")[-1].capitalize()+"Component }"

    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write("import {name} from './{path}.component';\n".format(name=name, path=path) + content)
    print('UPDATE - import Component to app.modules.ts')
    return "Imported succcessfully!"

def goalous():
    os.system("firefox --new-window 'https://isao.goalous.com/topics'")
    return ''

def dev(project):
    os.system('tmuxp load ~/projects/isao/projects/{project}/dev/session.yml'.format(project=project))

    
