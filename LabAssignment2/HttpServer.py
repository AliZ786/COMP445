import logging
import re
from FileManager import FileOperation

class HttpMethod:
    Get = "GET"
    Post = "POST"
    Invalid = "Invalid"

class FileOperation:
    Invalid = 0
    GetFileList = 1
    GetFileContent = 2
    GetResource = 3
    PostResource = 4
    PostFileContent = 5
    Download = 6

class HttpRequestParser:
    def __init__(self, request):
        # default values
        self.contentType = "application/json"
        self.operation = ''
        # split header and body of request
        self.http_header, self.http_body = request.split('\r\n\r\n')
        # get method, resource, version 
        header_lines = self.http_header.split('\r\n')
        self.method, self.resource, self.version = header_lines[0].split(' ')
        # get header info and set Content-Type
        self.dict_header_info = {}
        for line in header_lines[1:]:
            if re.match(r'Content-Type', line):
                self.contentType = line.split(':')[1]
            elif re.match(r'Content-Disposition', line):
                self.operation = FileOperation.Download
                if re.match(r'/(.+)', self.resource):
                    # ignore the first '/'
                    self.fileName = self.resource[1:]
            
            

        # set operation
        self._set_operation()


    def _set_operation(self):
        # GET method
        if self.method == HttpMethod.Get and self.operation != FileOperation.Download:
            # basic GET request
            if re.match(r'/get',self.resource):
                if self.resource in ['/get','/get?']:
                    self.param = ''
                else:
                    temp = self.resource.split('?')[-1]
                    result = {}
                    for item in temp.split('&'):
                        key, value = item.split('=')
                        result[key] = value
                    self.param = result   
                    logging.debug(f'Params : {result}')
                self.operation = FileOperation.GetResource

            elif self.resource == '/':
                self.operation = FileOperation.GetFileList
            else:
                if re.match(r'/(.+)', self.resource):
                    self.operation = FileOperation.GetFileContent
                    # ignore the first '/'
                    self.fileName = self.resource[1:]
                    logging.debug(f'FileName is : {self.fileName}')
                else:
                    self.operation = FileOperation.Invalid

        # POST method
        elif self.method == HttpMethod.Post:
            if self.resource == '/post':
                # set self data of body
                self.data = self.http_body
                self.operation = FileOperation.PostResource

            else:
                if re.match(r'/(.+)',self.resource):
                    # post file
                    self.fileName = self.resource[1:]
                    self.operation = FileOperation.PostFileContent
                    self.data = self.http_body
                else:
                    self.operation = FileOperation.Invalid
        elif self.operation == FileOperation.Download:
            pass
        # Invalid method
        else: 
            self.operation = FileOperation.Invalid