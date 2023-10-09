import datetime
import re
import json

class TimeManip(object):
    def __init__(self,Years = "True"):
        # Get the current date
        self.today = datetime.date.today()
        if Years == "False" :
            self.Week()
        else: 
            self.Years()
        print("Date start:", self.start)
        print("Date stop:", self.end)
        # Convert the dates to timestamps in milliseconds
        self.timestampstart = str(int(datetime.datetime.combine(self.start, datetime.time.min).timestamp() * 1000))
        self.timestampstop = str(int(datetime.datetime.combine(self.end, datetime.time.max).timestamp() * 1000))
        
    def Week(self):
        self.start = self.today - datetime.timedelta(days=self.today.weekday())
        self.end = self.start + datetime.timedelta(days=20)
        
    def Years(self):
        year = str(self.today.year)
        self.start = datetime.date.fromisoformat(str(self.today.year)+'-08-01')
        self.end = datetime.date.fromisoformat(str(self.today.year+1)+'-08-01')
        
class JsonManip(object):
    def __init__(self,json):
        self.data = json
        
    def extract(self,regex,groupe):
        match = re.search(regex, self.data)
        if match:
            self.data = match.group(groupe)
            
    def getdata(self):
        return json.loads(self.data)