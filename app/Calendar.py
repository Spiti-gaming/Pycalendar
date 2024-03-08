import pytz
import re
from icalendar import Calendar, Event, vCalAddress, vText
from dateutil import parser
from dataclasses import dataclass, field
import datetime


@dataclass
class Organizer:
    data_in: dict
    name: str or None = field(init=False)
    surname: str or None = field(init=False)
    email: str = field(init=False)

    def __post_init__(self):
        self.name = None
        self.surname = None
        for data_event in self.data_in:
            part_data = re.sub('[^A-Z]', '', data_event)
            if part_data == data_event:

                if self.surname is not None:
                    self.surname += '-' + data_event
                else:
                    self.surname = data_event
            else:
                if self.name is not None:
                    self.name += data_event
                else:
                    self.name = data_event
        self.email = f'{self.name}.{self.surname}@cpe.fr'

    def get_full_name(self) -> str:
        return f'{self.surname} {self.name}'


@dataclass
class EventInfo:
    data: dict

    summary: str = field(init=False)
    description: str = field(init=False)
    dtstart: datetime = field(init=False)
    dtend: datetime = field(init=False)
    location: str = field(init=False)
    organizer: vCalAddress or str = field(init=False)

    attendee: list[vCalAddress] = field(init=False)

    def __post_init__(self):
        self.dtstart = parser.parse(self.data['start']).astimezone(pytz.utc)
        self.dtend = parser.parse(self.data['end']).astimezone(pytz.utc)
        self.uid = self.data['id']
        self.data = self.data['title'].split('\n')
        self.attendee = []
        self.data[3] = self.data[3].replace(' ', '')
        self.summary = self.data[2]
        self.get_event_type_webaurion()

    def get_event_type_webaurion(self):

        if self.data[3] == "Cours" \
                or self.data[3] == "TP" \
                or self.data[3] == "TD" \
                or self.data[3] == "Langues" \

                or self.data[3] == "Examenmachine" \
                or self.data[3] == "Examenécrit" \
                or self.data[3] == "Projet":
            self.get_organizer()
        else:
            self.location = self.data[3]
            self.description = ""
            self.organizer = ""
            self.attendee = ""

    def get_organizer(self):

        if '/' in self.data[4]:
            teacher = self.data[4].split('/')[0]
        else:
            teacher = self.data[4]
        teacher = Organizer(teacher.split(' '))
        organizer = vCalAddress('MAILTO:' + teacher.email)
        organizer.params['cn'] = vText(teacher.get_full_name())
        organizer.params['role'] = vText('CHAIR')
        self.organizer = organizer
        teacher_required = f''
        self.description = self.data[3] + "\n"
        if '/' in self.data[4]:
            for member in self.data[4].split(' / '):
                teacher_acc = Organizer(member.split(' '))
                self.description += teacher_acc.get_full_name() + "\n"
                teacher_required += f',{teacher_acc.email}'
                teacher_addr = vCalAddress('MAILTO:' + teacher_acc.email)
                teacher_addr.params['cn'] = vText(teacher_acc.get_full_name())
                teacher_addr.params['ROLE'] = vText('REQ-PARTICIPANT')
                self.attendee.append(teacher_addr)
        else:
            self.description += teacher.get_full_name()

        attendee = vCalAddress('MAILTO:' + self.data[1] + '@cpe.fr')
        attendee.params['cn'] = vText(self.data[1])
        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
        self.attendee.append(attendee)
        self.location = self.data[0]


class CalendarTools:

    def __init__(self, auto=True):
        self.cal = Calendar()
        self.autonomie = auto

        self.cal.add('method', 'REQUEST')
        self.cal.add('prod_id', '-//Spiti Calendar//mycpe.cpe.fr')
        self.cal.add('version', '2.0')
        self.cal.add('calscale', "GREGORIAN")

    def add_to_calendar_from_webaurion(self, json_data):
        for event_calendar in json_data:
            event_info = EventInfo(event_calendar)
            e = Event()

            e.add('uid', event_info.uid)
            e.add('summary', event_info.summary)
            e.add('dtstart', event_info.dtstart)
            e.add('dtend', event_info.dtend)
            e.add('location', event_info.location)
            e.add('organizer', event_info.organizer)
            for element in event_info.attendee:
                e.add('attendee', element)
            e.add('description', event_info.description)

            if self.autonomie == True:
                self.cal.add_component(e)
            else:
                if event_info.data[3] != "Autonomie":
                    self.cal.add_component(e)

    def print_calendar_to_file(self, directory):
        with open(directory, 'wb') as f:
            print("Calendar File Created")
            f.write(self.cal.to_ical())


if __name__ == '__main__':
    data = {'id': '14184961',
            'title': '\n4IRC GR1\nAnglais S7\nLangues\nKRISTENOVA Lucie\nIntensive\n',
            'start': '2024-06-04T13:30:00+0200',
            'end': '2024-06-04T17:15:00+0200',
            'allDay': False,
            'editable': True,
            'className': 'N01_COURS_LANGUES'}

    event = EventInfo(data)
    print(event)
