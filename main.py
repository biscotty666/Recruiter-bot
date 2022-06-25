# !/usr/bin/python

#Prepare environment
import PIL.ImageDraw
import discord
import os
import regex
import yaml
from pathlib import Path # For paths
import platform # For stats
import logging
 
import time
import json
from discord.ext import commands # For discord

from datetime import datetime
from swgohhelp import SWGOHhelp, settings
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

#Get current working directory
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

#Defining a few things
secret_file = json.load(open(cwd+'/bot_config/secrets.json'))
RecBot = commands.Bot(command_prefix='/', case_insensitive=True)#, owner_id=271612318947868673)
RecBot.config_token = secret_file['token']
logging.basicConfig(level=logging.INFO)
RecBot.version = "0.1.0"

# filetoopen = str(cwd)+'/venv/config.yml'

# Fetch configuration variables
# with open(filetoopen) as file :
with open('bot_config/config.yml') as file :
    config = yaml.safe_load(file)


#Make the connection
creds = settings(config['CredName'], config['CredPass'], config['CredNum'], config['CredLet'])
client = SWGOHhelp(creds)

#Fetch the data
def GetGuildData():
    # Initialize some variables
    counter = 0
    guilds = []
    now = datetime.now()
    # print(now)

    # Create txt file
    f = open('OpenSlots.txt', 'w')
    f.write("Updated: " + str(now) + '\n')
    f.write('Name'.ljust(20) + 'GM'.rjust(7) + 'GP'.rjust(8) + '\n')
    f.close()



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

        # Add the rest of the info
        guilds.append({
            'GGp' : guildinfo['gp'],
            'GName' : guildinfo['name'],
            'GMembers' : guildinfo['members'],
        })

        f = open('OpenSlots.txt', "a")
        if guildinfo['members'] < 50 : f.write(str(guildinfo['name']).ljust(20) + str(guildinfo['members']).rjust(7) + str(round(guildinfo['gp']/1000000)).rjust(8)+'\n')
        f.close()

    return guilds

guilds = GetGuildData()

def GenerateSlide():

    #Create the Canvas object
    c = canvas.Canvas(config['RSFilename'])
    width = 640
    height = 360
    c.setPageSize((width, height))
    c.setTitle(config['RSTitle'])

    #Draw statically positioned items on canvas

    c.drawImage('RPBackground.jpg', 0, 0, width=width, height=height)
    c.setFont(config['Font'], config['FontSize'])
    c.setFillColor(colors.beige)
    c.drawCentredString(width/2, 330, config['RSTitle'])
    c.setFont(config['Font'], config['FontSize']-10)
    c.drawCentredString(width/2, 10, 'hello there')
    c.drawImage('Shard-Character-Ki-Adi-Mundi.png', 437, 300,width=20, height=20)
    c.drawImage('Shard-Character-Wat_Tambor.png', 512, 300,width=20, height=20)



    #populate data for the table
    #create first row of table
    data= [['', 'GP','DSTB', 'LSTB', 'CPit', '', '', 'GM']]
    #create the rest of the rows
    for guild in guilds :
        #modify appearance and content of items in guilds
        GPRounded = str(round(guild['GGp']/1000000))

        # This is to change the returned name into the name as printed
        # on the poster
        def GNameModify(name):
        # Remove the word Phantom and any of it's permutations
            name = regex.sub(r'Phant[oø?]+m\s*?', '', str(guild['GName']), 1)
        # Remove leading space
            name = regex.sub(r'^ ', '', name, 1)
        # Special bonus for Limb
            name = regex.sub(r'\?\?', 'i', name, 1)
            return name

        GNameModified = GNameModify('GName')
        DSTB = config['DSTB'][GNameModified]
        LSTB = config['LSTB'][GNameModified]
        CPIT = config['CPIT'][GNameModified]
        WAT = config['WAT'][GNameModified]
        KAM = config['KAM'][GNameModified]

        #create table row
        data.append([GNameModified, GPRounded, DSTB, LSTB, CPIT, WAT, KAM, guild['GMembers']])

    #create Table object based on data and add to image

    bcolor = Color(10,10,10,alpha=.5)

    table = Table(data, colWidths=[100,75,75,75,75,75,75], rowHeights=20)
    table.setStyle(TableStyle([

    # t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
    #                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))

        ('FONT',(0,0),(-1,-1), 'Helvetica-Bold', 22),
        ('TEXTCOLOR',(0,0),(-1,-1),colors.white),
        ('BOTTOMPADDING',(0,0),(-1,0),5),
        # set font and color for top row
        ('FONTSIZE',(0,0),(-1,0),16),
        ('TEXTCOLOR',(0,0),(-1,0),colors.beige),
        # set font size and color for first column
        ('FONTSIZE',(0,1),(0,-1),14),
        ('TEXTCOLOR',(0,1),(0,-1),colors.greenyellow),
        # set font size and color for second column
        ('FONTSIZE',(1,1),(1,-1),12),
        ('TEXTCOLOR',(1,1),(1,-1),colors.red),

        # set font size and color for fifth column
        ('FONTSIZE',(4,1),(4,-1),12),
        ('TEXTCOLOR',(4,1),(4,-1),colors.pink),
        ('BACKGROUND',(4,1),(4,-1),bcolor),
        # set font size and color for sixth and seventh columns
        ('FONTSIZE',(5,1),(6,-1),12),
        ('TEXTCOLOR',(5,1),(6,-1),colors.aqua),
        # set font size and color for eighth column
        ('FONTSIZE',(7,1),(7,-1),12),
        ('TEXTCOLOR',(7,1),(7,-1),colors.red),
        # ('ALIGN',(1,1), (1,-1),'RIGHT'),
        ('ALIGN',(1,0), (-1,-1),'CENTER'),
        ]))
    w, h = table.wrapOn(c, width, height)
    table.drawOn(c, 10, 305-h)

    c.showPage()
    c.save()



GenerateSlide()

# Generate png
def Makepng():
    images = convert_from_path('RecruitmentSlide.pdf')
    for image in images:
        image.save('RecruitmentSlide.png')



@RecBot.event
async def on_ready():
    print(f"-----\nLogged in as: {RecBot.user.name} : {RecBot.user.id}\n-----\nMy current prefix is: /\n-----")
    await RecBot.change_presence(activity=discord.Game(name=f"Hi, my names {RecBot.user.name}.\nUse / to interact with me!")) # This changes the bots 'activity'

@RecBot.command()
async def echo(ctx, *, message=None):
    """
    A simple command that repeats the users input back to them.
    """
    message = message or "Please provide the message to be repeated."
    await ctx.message.delete()
    await ctx.send(message)

@RecBot.command(name='UpdateData', aliases=['ud', 'du'])
async def UpdateData(ctx):
    """
    Refresh data from game server
    """
    try:
        await ctx.send('Fetching data. This may take a while')
        guilds = GetGuildData()
        await ctx.send('Data Updated')
    except:
        await ctx.send("Could not fetch data. Please try again")

@RecBot.command(name='GetRecruitmentSlide', aliases=['rs', 'recslide'])
async def GetRecruitmentSlide(ctx):
    """
    Get Recruitment Slide
    """
    try:
        Makepng()
        await ctx.send(file=discord.File('RecruitmentSlide.png'))
    except:
        await ctx.send("Could not fetch data. Please try again")

@RecBot.command(name='NeedMembers', aliases=['members', 'nm'])
async def UpdateData(ctx):
#     """
#     Get list of guilds needing members
#     """
    try:
        await ctx.send(file=discord.File('OpenSlots.txt'))
        with open("OpenSlots.txt") as f: 
            content = "\n".join(f.readlines())
        await ctx.send("```"+'\n' +content+'\n'+"```")
    except:
        await ctx.send("Oops")
#         guilds = GetGuildData()
#         await ctx.send('Data Updated')
#     except:
#         await ctx.send("Could not fetch data. Please try again")
        

RecBot.run(RecBot.config_token) #Runs our bot