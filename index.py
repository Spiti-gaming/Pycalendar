from WebAurion import WebAurion
from Tools import TimeManip, JsonManip
from Calendar import CalendarTools
import json



with open("config.json") as json_data_file:
    config = json.load(json_data_file)

timestamp = TimeManip(config['webaurion']['years'])




MyCpe = WebAurion(config['webaurion']['host'])


#===============================================================================
#       Login
#===============================================================================
payload = 'username='+config['webaurion']['username']+'&password='+config['webaurion']['password']+'&j_idt27='
if MyCpe.BaseRequest(payload,"/login",True) != True :
    exit("Error in connection")


#===============================================================================
#       Get Planning ID
#===============================================================================
payload='form=form&form%3AlargeurDivCenter=1620&form%3AidInit='+ MyCpe.formId+'&form%3Asauvegarde=&form%3Aj_idt817%3Aj_idt820_view=basicDay&form%3Aj_idt834%3Aj_idt838=&form%3Aj_idt834%3Atodos281544_selection=&form%3Aj_idt782%3Aj_idt784_dropdown=1&form%3Aj_idt782%3Aj_idt784_mobiledropdown=1&form%3Aj_idt782%3Aj_idt784_page=0&javax.faces.ViewState='+MyCpe.ViewState+'&form%3Asidebar=form%3Asidebar&form%3Asidebar_menuid=6'
if MyCpe.BaseRequest(payload,"/faces/MainMenuPage.xhtml",True) != True :
    exit("Error in connection")

#===============================================================================
#       Calendar Page
#===============================================================================
payload = 'javax.faces.partial.ajax=true&javax.faces.source=form%3Aj_idt118&javax.faces.partial.execute=form%3Aj_idt118&javax.faces.partial.render=form%3Aj_idt118&form%3Aj_idt118=form%3Aj_idt118&form%3Aj_idt118_start='+timestamp.timestampstart+'&form%3Aj_idt118_end='+timestamp.timestampstop+'&form=form&form%3AlargeurDivCenter=1620&form%3AidInit='+MyCpe.formId+'&form%3Adate_input=02%2F10%2F2023&form%3Aj_idt118_view=agendaWeek&form%3AoffsetFuseauNavigateur=-7200000&form%3Aonglets_activeIndex=0&form%3Aonglets_scrollState=0&javax.faces.ViewState='+MyCpe.ViewState
data_str = MyCpe.BaseRequest(payload,"/faces/Planning.xhtml",False)

json_data = JsonManip(data_str)
# Extract JSON data from CDATA section
json_data.extract(r'<update id="form:j_idt118"><!\[CDATA\[(.*?)\]\]></update>',1)
json_data.extract(r'{"events".*}',0)

# Convert JSON data to Python dictionary
data = json_data.getdata()




Calendar = CalendarTools(config['webaurion']['Autonomie'])

# Loop through the events and add them to the calendar

Calendar.AddToCalendarFromWebAurion(data['events'])

# Write the calendar to a file
Calendar.printCalendartofile(config['icsfile'])

