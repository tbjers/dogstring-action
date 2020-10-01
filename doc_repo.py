import os
import sys
import loguru
import copy
import requests
import json
from termcolor import colored
import tqdm 

def convert_py2string(PATH):
    filename = PATH
    with open(filename) as f:
        content = f.readlines()
    code = ''.join(content)
    return code

def add_doc2pyfile(doc_dict):
    PATH = doc_dict['path']
    code = doc_dict['code']
    f = open(PATH, "w+")
    f.write(code)
    f.close()



class DocRepo:
    def __init__(self, language, version):
        language = 'python'
        self.language = language

    def get_files_paths(self, repo_path):
            """Get list of testable files"""
            forbidden_words = []
            testable_files = []
            for path, subdirs, files in os.walk(repo_path):
                for name in files:
                    total_path = os.path.join(path, name)
                    if total_path.endswith('.py'):
                        add = True
                        for forbidden_word in forbidden_words:
                            if forbidden_word in total_path:
                                add = False
                        if add:
                            testable_files.append(os.path.abspath(total_path))
            return testable_files
        
    
    def get_docstring_dict(self, code_dict):
        url = 'https://ponicode-civet-beta.azurewebsites.net/suggest'
        r = requests.post(url, json=code_dict, timeout=600).json()
        return r

    def doc_repo(self, repo_path):
        """Add docstrings to all python files in the repo"""
        # Get python files paths
        filespaths = self.get_files_paths(repo_path)
        number_files = len(filespaths)
        loguru.logger.info(colored(f'{number_files} files found', 'green'))
        
        for path in tqdm.tqdm(filespaths):
            code_string = convert_py2string(path)
            code_dict = {"code": code_string, 'path': path}
            request = self.get_docstring_dict(code_dict)
            add_doc2pyfile(request)
            loguru.logger.info(colored(f'Add docstrings to a new file', 'green'))

    def doc_repo_from_commit(self, repo_path):
        """Add docstrings to all python files in the repo"""
        # Get python files paths
        with open('PATHS_TO_CHANGED_FILES.txt') as f:
            filespaths = f.readlines()
        f.close()
        os.remove('PATHS_TO_CHANGED_FILES.txt')
        number_files = len(filespaths)
        loguru.logger.info(colored(f'{number_files} files found', 'green'))
        for path in tqdm.tqdm(filespaths):
            path = path[:-1]
            if path.endswith('.py'):
                path = os.path.join(repo_path, path)
                code_string = convert_py2string(path)
                code_dict = {"code": code_string, 'path': path}
                request = self.get_docstring_dict(code_dict)
                add_doc2pyfile(request)
                loguru.logger.info(colored(f'Add docstrings to a new file', 'green'))


if __name__ == '__main__':
    repo_path = sys.argv[1]
    all_repo = sys.argv[2]
    repo_path = os.path.abspath(repo_path)
    version = '0.21.0'
    language = 'python'
    DR = DocRepo(language, version)
    if all_repo != 'false':
        DR.doc_repo(repo_path)
    else:
        DR.doc_repo_from_commit(repo_path)