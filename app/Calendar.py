import pytz
import re
from icalendar import Calendar, Event, vCalAddress, vText
from dateutil import parser


class CalendarTools:
    def __init__(self, auto=True):
        self.cal = Calendar()
        self.autonomie = auto
        self.cal.add('prod_id', '-//Spiti Calendar//mycpe.cpe.fr')
        self.cal.add('version', '2.0')

    def add_to_calendar_from_webaurion(self, json_data):
        for event in json_data:
            event_info = event['title'].split('\n')
            e = Event()
            e = self.event_type_webaurion(event_info, e)

            e.add('summary', event_info[2])
            start_time = parser.parse(event['start']).astimezone(pytz.utc)
            end_time = parser.parse(event['end']).astimezone(pytz.utc)
            e.add('dtstart', start_time)
            e.add('dtend', end_time)

            if self.autonomie:
                self.cal.add_component(e)
            else:
                if event_info[3] != "Autonomie":
                    self.cal.add_component(e)


    def event_type_webaurion(self, event_info, e):
        if event_info[3] == "Cours" \
                or event_info[3] == "TP" \
                or event_info[3] == "TD" \
                or event_info[3] == "Langues" \
                or event_info[3] == "Projet":

            e = self.data_with_organizer(e, event_info)
        else:
            e.add('location', event_info[3])
            e.add('description', "")
        return e

    def data_with_organizer(self,e, event_info):
        # Refactor organiser

        teacher = self.name_printable(event_info[4].split(' '))
        organizer = vCalAddress('MAILTO:'+teacher[0]+'.'+teacher[1]+"@cpe.fr")
        organizer.params['cn'] = vText(event_info[1])
        organizer.params['role'] = vText('CHAIR')
        e['organizer'] = organizer

        attendee = vCalAddress('MAILTO:'+event_info[1]+'@cpe.fr')
        attendee.params['cn'] = vText(event_info[1])
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')

        e.add('attendee', attendee, encode=0)
        e.add('description', event_info[3] + "\n" + teacher[1] +' '+teacher[0])
        e.add('location', event_info[0])
        return e

    @staticmethod
    def name_printable(name_in):
        name = None
        surname = None
        for data in name_in:
            part_data = re.sub('[^A-Z]', '', data)
            if part_data == data:
                if surname is not None:
                    surname += '-'+data
                else:
                    surname = data
            else:
                if name is not None:
                    name += data
                else:
                    name = data
        return [name, surname]

    def print_calendar_to_file(self, directory):
        with open(directory, 'wb') as f:
            print("Calendar File Created")
            f.write(self.cal.to_ical())
