import http.client
import json
from dataclasses import dataclass, field
from dateutil import parser
from datetime import datetime
import datetime as dt
from icalendar import Calendar, Event, vCalAddress, vText
import pytz




@dataclass
class EventInfo:
    data: dict
    summary: str = field(init=False)
    description: str = field(init=False)
    dtstart: datetime = field(init=False)
    dtend: datetime = field(init=False)
    location: str = field(init=False)
    organizer: vCalAddress or str = field(init=False)
    event_type: str = field(init=False)


    def __post_init__(self):
        self.dtstart = parser.parse(self.data['date_debut']).astimezone(pytz.utc)
        self.dtend = parser.parse(self.data['date_fin']).astimezone(pytz.utc)
        self.location = self.data['ressource']
        if self.data['description'] is None:
            self.summary = self.data['favori']["f3"]
        else:
            self.summary = self.data['description']

        self.event_type = self.data['type_activite']
        self.description = self.data['favori']["f3"]
        self.organizer = self.data['intervenants']
        self.data = None

class CalendarTools:

    def __init__(self, auto=True):
        self.cal = Calendar()
        self.autonomie = auto
        self.cal.add('prod_id', '-//Spiti Calendar//mycpe.cpe.fr')
        self.cal.add('version', '2.0')

    def add_to_calendar_from_webaurion(self, json_data):
        for event_calendar in json_data:
            if event_calendar['type_activite']:

                event_info = EventInfo(event_calendar)
                e = Event()
                e.add('summary', event_info.summary)
                e.add('dtstart', event_info.dtstart)
                e.add('dtend', event_info.dtend)
                e.add('location', event_info.location)
                e.add('organizer', event_info.organizer)
                e.add('description', event_info.description)

                if self.autonomie:
                    self.cal.add_component(e)
                else:
                    if event_info.event_type == "Autonomie":
                        self.cal.add_component(e)

    def print_calendar_to_file(self, directory):
        with open(directory, 'wb') as f:
            print("Calendar File Created")
            f.write(self.cal.to_ical())


def years():

    start = dt.date.fromisoformat(str(datetime.today().year) + '-08-01')
    end = dt.date.fromisoformat(str(datetime.today().year + 1) + '-08-01')
    return start, end


def week():
    start = datetime.today() - dt.timedelta(days=datetime.today().weekday())
    end = start + dt.timedelta(days=20)

    return start, end


with open("../config.json") as f:
    config = json.load(f)

conn = http.client.HTTPSConnection(config['webaurion']['host'])
payload = 'username='+config['webaurion']['username']+'&password='+config['webaurion']['password']
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}
conn.request("POST", "/login", payload, headers)
res = conn.getresponse()
data = res.read()

headers['Cookie'] = res.getheader('Set-Cookie').split(";")[0]

if config['webaurion']['years']:
    start, end = years()
else:
    start, end = week()

conn.request("GET", f"/mobile/mon_planning?date_debut={start}&date_fin={end}", "", headers)
res = conn.getresponse()
data2 = res.read()
data_json = json.loads(data2.decode("utf-8"))
calender = CalendarTools()
calendrier = calender.add_to_calendar_from_webaurion(data_json)

calender.print_calendar_to_file(config['icsfile'])
conn.close()