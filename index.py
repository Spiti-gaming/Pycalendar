import http.client
import re
import json
import pytz
from icalendar import Calendar, Event, vCalAddress, vText
from dateutil import parser
import datetime


with open("config.json") as json_data_file:
    config = json.load(json_data_file)



# Get the current date
today = datetime.date.today()

# Calculate the date of the first day of the current week (Monday)
monday = today - datetime.timedelta(days=today.weekday())

# Calculate the date of the last day of the following week (Sunday)
sunday = monday + datetime.timedelta(days=20)

# Convert the dates to timestamps in milliseconds
timestampstart = str(int(datetime.datetime.combine(monday, datetime.time.min).timestamp() * 1000))
timestampstop = str(int(datetime.datetime.combine(sunday, datetime.time.max).timestamp() * 1000))

print("Timestamp start:", timestampstart)
print("Timestamp stop:", timestampstop)




conn = http.client.HTTPSConnection(config['webaurion']['host'])
payload = 'username='+config['webaurion']['username']+'&password='+config['webaurion']['password']+'&j_idt27='

headers = {
    'Host': config['webaurion']['host'],
    'Referer': 'https://'+config['webaurion']['host']+'/faces/Login.xhtml',
    'Content-Type': 'application/x-www-form-urlencoded',
    'allow_redirects':False
}


#===============================================================================
#       Login
#===============================================================================
conn.request("POST", "/login", payload, headers)
res = conn.getresponse()
res.read()
cookie = res.getheader('Set-Cookie')
headers['Cookie'] = cookie
formId = None
ViewState=None
# Follow the redirection
if res.status == 302:
        location = res.getheader('Location')
        print(location)
        conn.request("GET", location,payload, headers)
        res = conn.getresponse()
        data = res.read()
        data_str = data.decode("utf-8")
        # Extract the value of the input with name "form:idInit"
        match = re.search(r'<input.*?name="form:idInit".*?value="(.*?)".*?>', data_str)
        if match:
            formId = match.group(1)
            print("Form ID :"+formId)
        else :
             exit("Error: form:idInit not found")
        match = re.search(r'<input.*?name="javax.faces.ViewState".*?value="(.*?)".*?>', data_str)
        if match:
            ViewState = match.group(1)
            print("JavaViewState :"+ViewState)
else:
    print("Error: status code is not 302")
    exit("Error: status code is not 302")



#===============================================================================
#       Get Planning ID
#===============================================================================
cookie = headers['Cookie'].split(";")[0]
newheaders = {
  'Host': headers['Host'],
  'Referer': "https://"+headers['Host']+"/",
  'Sec-Fetch-Mode': 'navigate',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': cookie
}
payload='form=form&form%3AlargeurDivCenter=1620&form%3AidInit='+formId+'&form%3Asauvegarde=&form%3Aj_idt817%3Aj_idt820_view=basicDay&form%3Aj_idt834%3Aj_idt838=&form%3Aj_idt834%3Atodos281544_selection=&form%3Aj_idt782%3Aj_idt784_dropdown=1&form%3Aj_idt782%3Aj_idt784_mobiledropdown=1&form%3Aj_idt782%3Aj_idt784_page=0&javax.faces.ViewState='+ViewState+'&form%3Asidebar=form%3Asidebar&form%3Asidebar_menuid=6'
conn.request("POST", "/faces/MainMenuPage.xhtml", str(payload), newheaders)#https://mycpe.cpe.fr/faces/MainMenuPage.xhtml
res = conn.getresponse()
res.read()
# Follow the redirection
if res.status == 302:
        location = res.getheader('Location')
        print(location)
        conn.request("GET", location,payload, newheaders)
        res = conn.getresponse()
        data = res.read()
        data_str = data.decode("utf-8")
        # Extract the value of the input with name "form:idInit"
        match = re.search(r'<input.*?name="form:idInit".*?value="(.*?)".*?>', data_str)
        if match:
            formId = match.group(1)
            print("Form ID :"+formId)
        match = re.search(r'<input.*?name="javax.faces.ViewState".*?value="(.*?)".*?>', data_str)
        if match:
            ViewState = match.group(1)
            print("JavaViewState :"+ViewState)
else:
    print("Error: status code is not 302")


# Use the cookie of the first request
cookie = res.getheader('Set-Cookie')
headers['Cookie'] = cookie

#===============================================================================
#       Calendar Page
#===============================================================================
json_data = None
payload = 'javax.faces.partial.ajax=true&javax.faces.source=form%3Aj_idt118&javax.faces.partial.execute=form%3Aj_idt118&javax.faces.partial.render=form%3Aj_idt118&form%3Aj_idt118=form%3Aj_idt118&form%3Aj_idt118_start='+timestampstart+'&form%3Aj_idt118_end='+timestampstop+'&form=form&form%3AlargeurDivCenter=1620&form%3AidInit='+formId+'&form%3Adate_input=02%2F10%2F2023&form%3Aj_idt118_view=agendaWeek&form%3AoffsetFuseauNavigateur=-7200000&form%3Aonglets_activeIndex=0&form%3Aonglets_scrollState=0&javax.faces.ViewState='+ViewState
conn.request("POST", "/faces/Planning.xhtml", str(payload), newheaders)#	https://mycpe.cpe.fr/faces/Planning.xhtml
res = conn.getresponse()
data = res.read()
data_str= data.decode("utf-8")

# Extract JSON data from CDATA section
match = re.search(r'<update id="form:j_idt118"><!\[CDATA\[(.*?)\]\]></update>', data_str)
if match:
    cdata = match.group(1)
    json_match = re.search(r'{"events".*}', cdata)
    if json_match:
        json_data = json_match.group(0)


# Convert JSON data to Python dictionary
data = json.loads(json_data)

# Create a new iCalendar file
cal = Calendar()
# Set the calendar properties
cal.add('prodid', '-//Spiti Calendar//mycpe.cpe.fr//')
cal.add('version', '2.0')

# Loop through the events and add them to the calendar

for event in data['events']:
    EventInfo = event['title'].split('\n')
    # Create a new event
    e = Event()
    if EventInfo[3] == "Autonomie":
        e.add('location', EventInfo[3])
        e.add('description', "")
    else :
        # Edit data for Teacher
        Teacher = EventInfo[4].split(' ')
        TeacherName = Teacher[1]
        for i in range(2,Teacher.__len__()):
            TeacherName = TeacherName +"-"+ Teacher[i]
        organizer = vCalAddress('MAILTO:'+TeacherName+'.'+Teacher[0]+'@cpe.fr')
        organizer.params['cn'] = vText(EventInfo[4])
        organizer.params['role'] = vText('CHAIR')
        e['organizer'] = organizer

        # Add Participate (class)
        attendee = vCalAddress('MAILTO:'+EventInfo[1]+'@cpe.fr')

        attendee.params['cn'] = vText(EventInfo[1])

        attendee.params['ROLE'] = vText('REQ-PARTICIPANT')

        e.add('attendee', attendee, encode=0)
        e.add('description', EventInfo[3] + "\n" + EventInfo[4])
        e.add('location', EventInfo[0])

    # Set the event properties
    
    e.add('summary', EventInfo[2])

    # Set the start and end times
    start_time = parser.parse(event['start']).astimezone(pytz.utc)
    end_time = parser.parse(event['end']).astimezone(pytz.utc)
    e.add('dtstart', start_time)
    e.add('dtend', end_time)

    # Add the event to the calendar
    cal.add_component(e)

# Write the calendar to a file
with open(config['icsfile'], 'wb') as f:
    f.write(cal.to_ical())

