from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from dateutil import parser
import re

class CalendarTools(object):
    def __init__(self,Auto="True"):
        self.cal = Calendar()
        self.autonomie = Auto
        # Set the calendar properties
        self.cal.add('prodid', '-//Spiti Calendar//mycpe.cpe.fr//')
        self.cal.add('version', '2.0')
        
    def AddToCalendarFromWebAurion(self,json):
        for event in json:
            EventInfo = event['title'].split('\n')
            # Create a new event
            e = Event()
            e = self.eventTypeWebAurion(EventInfo, e)

            # Set the event properties
            
            e.add('summary', EventInfo[2])

            # Set the start and end times
            start_time = parser.parse(event['start']).astimezone(pytz.utc)
            end_time = parser.parse(event['end']).astimezone(pytz.utc)
            e.add('dtstart', start_time)
            e.add('dtend', end_time)

            # Add the event to the calendar
            if self.autonomie =="True":
                self.cal.add_component(e)
            else:
                if EventInfo[3] != "Autonomie":
                    self.cal.add_component(e)
            
    def eventTypeWebAurion(self,EventInfo,e):
        EventInfo[3] = EventInfo[3].replace(' ','')
        if EventInfo[3] =="Cours" or EventInfo[3] == "TP" or EventInfo[3] == "TD" or EventInfo[3] == "Langues" or EventInfo[3] == "Projet" :
            e = self.DataWithOrganizer(e,EventInfo)
        else:
            e.add('location', EventInfo[3])
            e.add('description', "")
        return e
    
    def DataWithOrganizer(self,e,EventInfo):
        # Edit data for Teacher
        Teacher = self.NamePrintable(EventInfo[4].split(' '))
        organizer = vCalAddress('MAILTO:'+Teacher[0]+'.'+Teacher[1]+'@cpe.fr')
        organizer.params['cn'] = vText(EventInfo[4])
        organizer.params['role'] = vText('CHAIR')
        e['organizer'] = organizer

        # Add Participate (class)
        attendee = vCalAddress('MAILTO:'+EventInfo[1]+'@cpe.fr')

        attendee.params['cn'] = vText(EventInfo[1])

        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')

        e.add('attendee', attendee, encode=0)
        e.add('description', EventInfo[3] + "\n" + Teacher[1]+' '+Teacher[0])
        e.add('location', EventInfo[0])
        return e
    
    def NamePrintable(self,name):
        Name = None
        SurName = None
        for data in name:
            partData = re.sub('[^A-Z]', '',data)
            if(partData == data):
                if SurName != None:
                    SurName += '-'+data
                else:
                    SurName = data
            else:
                if Name != None:
                    Name += '-'+data
                else:
                    Name = data
        return [Name, SurName]
        
    
    
    def printCalendartofile(self, dir):
        with open(dir, 'wb') as f:
            print("Calendar File Create")
            f.write(self.cal.to_ical())
