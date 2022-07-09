# Prepare environment

# Discord
import discord
from discord.ext import tasks, commands
import platform
import logging

# General commands and utilities
import os
import regex
import yaml
from pathlib import Path
import time
from datetime import datetime
import json

# For interaction with game api
from swgohhelp import SWGOHhelp, settings

# Image and pdf
import PIL.ImageDraw
from reportlab.pdfgen import canvas, pdfimages
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, cm
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from PIL import Image, ImageDraw
from pdf2image import convert_from_path

# Prepare custom fonts
pdfmetrics.registerFont(TTFont('Trickster', 'Trickster-Reg.ttf'))
pdfmetrics.registerFont(TTFont('Vampire', 'Vampire Wars.ttf'))

# Get current working directory
cwd = Path(__file__).parents[0]
cwd = str(cwd)

# Load configuration variables
with open('config.yml') as file :
    config = yaml.safe_load(file)

# Make the connection
creds = settings(config['CredName'], config['CredPass'], config['CredNum'], config['CredLet'])
client = SWGOHhelp(creds)

# This is to change the returned name into the name as printed
# on the poster
def GNameModify(name):
    # Remove the word Phantom and any of it's permutations
    name = regex.sub(r'Phant[oø?]+m\s*?', '', name, 1)
    # Remove leading space
    name = regex.sub(r'^ ', '', name, 1)
    # Special bonus for Limb
    name = regex.sub(r'\?\?', 'i', name, 1)
    return name


# Fetch the data
def GetGuildData():
    # Initialize some variables
    counter = 0
    guilds = []
    now = datetime.now()
 
    # Initialize txt file with some header info
    f = open('OpenSlots.txt', 'w')
    f.write("Updated: " + str(now) + '\n\n')
    f.write('Name'.ljust(20) + 'GM'.rjust(7) + 'GP'.rjust(8) + '\n')
    f.close

    # Make the calls and populate guilds
    for allycode in config['allycodes'] :
        counter += 1
        print('This is pass ', counter, '/14')
        def GetData():
            try:
                print('Trying')
                response = client.get_data('guild', allycode)
                if response == ' None ':
                    GetData()
                return response
            except Exception as e:
                time.sleep(15)
                GetData()

        response = GetData()
        guildinfo = response[0]

        # Add the info to populate guilds for use in drawing the slide
        guilds.append({
            'GGp' : guildinfo['gp'],
            'GName' : GNameModify(guildinfo['name']),
            'GMembers' : guildinfo['members'],
        })

        # Add info to the OpenSlots.txt for guilds needing members
        f = open('OpenSlots.txt', "a")
        if guildinfo['members'] < 50:
            f.write(str(GNameModify(guildinfo['name'])).ljust(20) + str(guildinfo['members']).rjust(7) + str(round(guildinfo['gp']/1000000)).rjust(8)+'\n')
        f.close()

    return guilds

guilds = GetGuildData()

return guilds
print(guilds)


# # Generate the slide from data in guilds
# def GenerateSlide():

#     #Create and configure the Canvas object
#     c = canvas.Canvas(config['RSFilename'])
#     width = 640
#     height = 360
#     c.setPageSize((width, height))
#     c.setTitle(config['RSTitle'])

#     # Draw statically positioned items on canvas

#     # Add background image
#     c.drawImage('RPBackgroun.jpeg', 0, 0, width=width, height=height)

#     # Add title/alliance name
#     c.setFont(config['Font'], config['FontSize'])
#     c.setFillColor(colors.orangered)
#     c.drawCentredString(width/2, 330, config['RSTitle'])

#     # Place icons at top of two columns
#     c.drawImage('Shard-Character-Ki-Adi-Mundi.png', 440, 300,width=15, height=15)
#     c.drawImage('Shard-Character-Wat_Tambor.png', 515, 300,width=15 , height=15)

#     # Populate data for the table

#     # Create first row of table
#     data= [['', 'GP','DSTB', 'LSTB', 'CPit', '', '', 'GM']]

#     # Create the rest of the rows
#     for guild in guilds :
#         # Modify appearance and content of items in guilds
#         GPRounded = str(round(guild['GGp']/1000000))
#         GNameModified = GNameModify(guild['GName'])
#         DSTB = config['DSTB'][GNameModified]
#         LSTB = config['LSTB'][GNameModified]
#         CPIT = config['CPIT'][GNameModified]
#         WAT = config['WAT'][GNameModified]
#         KAM = config['KAM'][GNameModified]

#         #create table row
#         data.append([GNameModified, GPRounded, DSTB, LSTB, CPIT, WAT, KAM, guild['GMembers']])

#     # Create Table object based on data and add to image
#     table = Table(data, colWidths=[100,75,75,75,75,75,75], rowHeights=20)
#     table.setStyle(TableStyle([
#         ('FONT',(0,0),(-1,-1), 'Helvetica-Bold', 18),
#         ('TEXTCOLOR',(0,0),(-1,-1),colors.white),
#         ('BOTTOMPADDING',(0,0),(-1,0),8),
#         # set font and color for top row
#         ('FONTSIZE',(0,0),(-1,0),18),
#         ('TEXTCOLOR',(0,0),(-1,0),colors.cyan),
#         # set font size and color for first column
#         ('FONTSIZE',(0,1),(0,-1),18),
#         ('TEXTCOLOR',(0,1),(0,-1),colors.cyan),
#         # set font size and color for second column
#         ('FONTSIZE',(1,1),(1,-1),16),
#         ('TEXTCOLOR',(1,1),(1,-1),colors.whitesmoke),
#         # set font size and color for third and fourth column
#         ('FONTSIZE',(2,1),(3,-1),16),
#         ('TEXTCOLOR',(2,1),(3,-1),colors.whitesmoke),
#         # set font size and color for fifth column
#         ('FONTSIZE',(4,1),(4,-1),16),
#         ('TEXTCOLOR',(4,1),(4,-1),colors.whitesmoke),
#         # set font size and color for sixth and seventh columns
#         ('FONTSIZE',(5,1),(6,-1),16),
#         ('TEXTCOLOR',(5,1),(6,-1),colors.whitesmoke),
#         # set font size and color for eighth column
#         ('FONTSIZE',(7,1),(7,-1),16),
#         ('TEXTCOLOR',(7,1),(7,-1),colors.whitesmoke),
#         # ('ALIGN',(1,1), (1,-1),'RIGHT'),
#         ('ALIGN',(1,0), (-1,-1),'CENTER'),
#         ]))
#     w, h = table.wrapOn(c, width, height)
#     table.drawOn(c, 10, 310-h)

#     c.showPage()
#     c.save()

# GenerateSlide()

# # Convert slide to png
# images = convert_from_path('RecruitmentSlide.pdf')
# for image in images:
#     image.save('RecruitmentSlide.png')

# # Create and launch discord bot

# # Defining a few things and creating RecBot
# secret_file = json.load(open(cwd+'/bot_config/secrets.json'))
# RecBot = commands.Bot(command_prefix='/', case_insensitive=True)#, owner_id=271612318947868673)
# RecBot.config_token = secret_file['token']
# logging.basicConfig(level=logging.INFO)
# RecBot.version = "0.1.0"

# # Prepare content for need members message
# with open("OpenSlots.txt") as f: content = "\n".join(f.readlines())

# # Commands to initialize bot
# @RecBot.event
# async def on_ready():
#     print(f"-----\nLogged in as: {RecBot.user.name} : {RecBot.user.id}\n-----\nMy current prefix is: /\n-----")
#     await RecBot.change_presence(activity=discord.Game(name=f"Hi, my names {RecBot.user.name}.\nUse / to interact with me!"))

# # Command to update data from api
# @RecBot.command(name='UpdateData', aliases=['ud', 'du'])
# async def UpdateData(ctx):
#     """
#     Refresh data from game server
#     """
#     try:
#         await ctx.send('Fetching data. This may take a while')
#         guilds = GetGuildData()
#         await ctx.send('Data Updated')
#     except:
#         await ctx.send("Could not fetch data. Trying again.")

# # Command to send png
# @RecBot.command(name='GetRecruitmentSlide', aliases=['rs', 'recslide'])
# async def GetRecruitmentSlide(ctx):
#     """
#     Get Recruitment Slide
#     """
#     try:
#         await ctx.send(file=discord.File('RecruitmentSlide.png'))
#     except:
#         await ctx.send("Could not fetch data. Please try again")

# # Command to send report on guilds needing members
# @RecBot.command(name='NeedMembers', aliases=['members', 'nm'])
# async def NeedMembers(ctx):
# #     """
# #     Get list of guilds needing members
# #     """
#     try:
#         with open("OpenSlots.txt") as f: 
#             content = "\n".join(f.readlines())
#         await ctx.send("```"+'\n' +content+'\n'+"```")
#     except:
#         await ctx.send("Oops")

# # Loop to regularly send need members info
# @tasks.loop(hours=12)
# async def TestLoop():
#     await RecBot.mychannel.send("```"+'\n' +content+'\n'+"```")

# @TestLoop.before_loop
# async def before_TestLoop():
#     await RecBot.wait_until_ready()
#     RecBot.mychannel = RecBot.get_channel(991738419476701309)

# TestLoop.start()

# # Fire up the bot        
# RecBot.run(RecBot.config_token) #Runs our bot