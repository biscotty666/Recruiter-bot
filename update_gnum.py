import regex
import yaml
import time
from swgohhelp import SWGOHhelp, settings
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, cm
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from PIL import Image, ImageDraw
pdfmetrics.registerFont(TTFont('Trickster', 'Trickster-Reg.ttf'))
pdfmetrics.registerFont(TTFont('Vampire', 'Vampire Wars.ttf'))
import datetime
from keep_alive import keep_alive
from pdf2image import convert_from_path


def update_gnum():
  f = open('OpenSlots.txt', "w")
  f.close()

#Discord interactions aka slash commands 
#bot = interactions.Client(token='DISCORD_TOKEN')

# Fetch configuration variables
  with open('config.yml') as file :
      config = yaml.safe_load(file)

#Fetch guild data from game. From the raw data populate guilds

#Make the connection
  creds = settings(config['CredName'], config['CredPass'], config['CredNum'], config['CredLet'])
  client = SWGOHhelp(creds)

#Fetch the data
  guilds = []
  NumPass = 1
# f = open('OpenSlots.txt', "w")
# f.close()

#Clear OpenSlots file because Replit doesnt like the close function

  w = open('OpenSlots.txt', "w")
  w.write("")   
  w.close()


 
  
  f = open('OpenSlots.txt', 'a')


# f.write('Name\tMembers\tGP\n')
  f.write('Name'.ljust(15) + 'Members'.rjust(7) + 'GP'.rjust(8) + '\n')
  f.close()
  for allycode in config['allycodes'] :
      def GetData():
          try: 
              print('Trying to get guild data', NumPass, '/14')
              response = client.get_data('guild', allycode)
            #print(response)
              return response
          except:
              print('Waiting 20 secs')
              time.sleep(20)
              GetData()
        

    # extract dictionary from list
      try:
          guildinfo = GetData()
          guildinfo = guildinfo[0]
      except:
          print('Bad data, try again')
          GetData()

 
      if type(guildinfo) == 'NoneType':
          print('Empty Response')
          GetData()
 
    # Add the rest of the info
      try:
          NameProcessed = guildinfo['name']
      except:
          print('Even more bad data')
          GetData()


    # Convert database version to human readable
      NameProcessed = regex.sub(r'Phant[oø?]+m\s*?', '', NameProcessed, 1)
      NameProcessed = regex.sub(r'^ ', '', NameProcessed, 1)
      NameProcessed = regex.sub(r'\?\?', 'i', NameProcessed, 1)

    # Populate the guilds dictionary
      guilds.append({
        'GGp' : guildinfo['gp'],
        'GName' : NameProcessed,
        'GMembers' : guildinfo['members'],
        'GRaid' : guildinfo['raid'],
        'AllyCode' : allycode,
      })

    # Generate text file to list guilds with membership below 50


      f = open('OpenSlots.txt', "a")
      if guildinfo['members'] < 50 : f.write(NameProcessed.ljust(15) + str(guildinfo['members']).rjust(5) + str(round(guildinfo['gp']/1000000)).rjust(10)+'\n')
      f.close()
    
 
      print('Success!')
      NumPass += 1
  #Add time marker to OpenSlots
  now = datetime.datetime.now() - datetime.timedelta(hours = 5)
  t = open('OpenSlots.txt', "a")
  t.write("Updated: "+ now.strftime("%Y-%m-%d %H:%M:%S"+" CST " + '\n'))
  t.close() 