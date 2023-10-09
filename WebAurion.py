
import http.client
import re

class WebAurion(object):
    def __init__(self, host):
        self.conn = http.client.HTTPSConnection(host)
        self.formId = None
        self.ViewState = None
        self.headers = {
            'Host': host,
            'Referer': "https://"+host+"/",
            'Sec-Fetch-Mode': 'navigate',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
    def FormID(self):
        return self.FormID
    
    def viewState(self):
        return self.ViewState
        
    def BaseRequest(self, payload,location, followRedirect = False):
        self.conn.request("POST", location, payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        cookie = res.getheader('Set-Cookie')
        if cookie != None:
            self.headers['Cookie'] = cookie.split(";")[0]
        if followRedirect == False :
            return data.decode("utf-8")
        if res.status != 302:
            return -1
        self.redirection(res,payload)
        return True

    def redirection(self,res,payload):
        location = res.getheader('Location')
        print("Redirect to :"+location)
        self.conn.request("GET", location,payload, self.headers)
        res = self.conn.getresponse()
        data = res.read()
        data_str = data.decode("utf-8")
        # Extract the value of the input with name "form:idInit"
        match = re.search(r'<input.*?name="form:idInit".*?value="(.*?)".*?>', data_str)
        if match:
            self.formId = match.group(1)
            #print("Form ID :"+self.formId)
        else :
             exit("Error: form:idInit not found")
             
        # Extract the value of the input with name "javax.faces.ViewState"
        match = re.search(r'<input.*?name="javax.faces.ViewState".*?value="(.*?)".*?>', data_str)
        if match:
            self.ViewState = match.group(1)
            #print("JavaViewState :"+self.ViewState)
        else :
             exit("Error: JavaViewState not found")
        return True