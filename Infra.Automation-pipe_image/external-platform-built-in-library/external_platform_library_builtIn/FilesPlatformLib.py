import yaml
import os

class FilesPlatformLib():

    def get_services_list_for_deploy(self, file_name):
        file1 = open(file_name, "r")
        list_services = []
        while True:
            line = file1.readline()
            if 'true' in line:
                list_services.append(line.strip().split(':')[0])
            elif not line:
                break
        return list_services

    def get_namespaces_for_deploy(self, file_name):
        list_services = self.get_services_list_for_deploy(file_name)
        file2 = open(file_name, "r")
        namespaces = []
        while True:
            line = file2.readline()
            if '_ns' in line:
                for service in list_services:
                    if service in line:
                        namespaces.append(line.strip().split(': ')[1].replace('"', ''))
            elif not line:
                break
        return namespaces

    def getFiles(self, path, files=[]):
        if os.path.isfile(path):
            return files.append(path)
        for item in os.listdir(path):
            item = os.path.join(path, item)
            if os.path.isfile(item):
                files.append(item)
            else:
                files = self.getFiles(item, files)
        return files

    def get_files(self, path):
        files = []
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                files.append(os.path.join(dirpath, file))
        return files

    def get_namespaces_names(self, array_files, cloudprefix):
        namespaces_names = list()
        for file_path in array_files:
            if cloudprefix in file_path:
                body = yaml.safe_load(open(file_path))
                namespaces_names.append((body.get('PROJECT')).replace(cloudprefix + '-', ''))
        return namespaces_names

    def get_resources_name(self, array_files):
        clusterroles_names = list()
        for file_path in array_files:
            body = yaml.safe_load(open(file_path))
            clusterroles_names.append((body.get('metadata')).get('name'))
        return clusterroles_names

    def got_apiVersion_for_crd(self, path):
        with open(path, 'r') as file:
            crd = file.read()
            crd = crd.split("\n")[0]
            return (crd.replace((crd.partition('/')[0]),'')).replace('/','')
