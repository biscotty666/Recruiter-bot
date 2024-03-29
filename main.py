# !/usr/bin/python

#Prepare environment
import PIL.ImageDraw
import discord
from discord.ext import tasks
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
# print(f"{cwd}\n-----")

# Fetch configuration variables
with open('config.yml') as file :
    config = yaml.safe_load(file)

#Make the connection
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


#Fetch the data
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

    # rt pdf to png

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

        # Add the rest of the info
        guilds.append({
            'GGp' : guildinfo['gp'],
            'GName' : GNameModify(guildinfo['name']),
            'GMembers' : guildinfo['members'],
        })

        # Add infor to the OpenSlots.txt
        f = open('OpenSlots.txt', "a")
        if guildinfo['members'] < 50:
            # f.write(str(guilds['GName']).ljust(20) + str(guilds['GMembers']).rjust(7) + str(round(guilds['GGp']/1000000)).rjust(8) + '/n')
            f.write(str(GNameModify(guildinfo['name'])).ljust(20) + str(guildinfo['members']).rjust(7) + str(round(guildinfo['gp']/1000000)).rjust(8)+'\n')
        f.close()

    return guilds

guilds = GetGuildData()


# Generate the slide from data in guilds
def GenerateSlide():

    #Create the Canvas object
    c = canvas.Canvas(config['RSFilename'])
    width = 640
    height = 360
    c.setPageSize((width, height))
    c.setTitle(config['RSTitle'])
    im = Image.open('RPBackground.jpg')
    im_rgba = im.copy()
    im_rgba.putalpha(200)
    im_rgba.save('RPBackground.png')

    #Draw statically positioned items on canvas

    c.drawImage('RPBackgroun.jpeg', 0, 0, width=width, height=height)
    # c.drawImage('image.jpg', width=width, height=height)

    c.setFont(config['Font'], config['FontSize'])
    c.setFillColor(colors.orangered)
    c.drawCentredString(width/2, 330, config['RSTitle'])
    # c.setFont(config['Font'], config['FontSize']-14)
    # c.drawCentredString(width/2, 10, 'hello there')
    c.drawImage('Shard-Character-Ki-Adi-Mundi.png', 440, 300,width=15, height=15)
    c.drawImage('Shard-Character-Wat_Tambor.png', 515, 300,width=15 , height=15)

    #populate data for the table
    #create first row of table
    data= [['', 'GP','DSTB', 'LSTB', 'CPit', '', '', 'GM']]

    #create the rest of the rows
    for guild in guilds :
        #modify appearance and content of items in guilds
        GPRounded = str(round(guild['GGp']/1000000))

 
        GNameModified = GNameModify(guild['GName'])
        
        # GName = GNameModify('GName')

        DSTB = config['DSTB'][GNameModified]
        LSTB = config['LSTB'][GNameModified]
        CPIT = config['CPIT'][GNameModified]
        WAT = config['WAT'][GNameModified]
        KAM = config['KAM'][GNameModified]

        #create table row
        data.append([GNameModified, GPRounded, DSTB, LSTB, CPIT, WAT, KAM, guild['GMembers']])

    #create Table object based on data and add to image

    bcolor = Color(10,10,10,alpha=.5)
    # rgbYellow = Color()

    table = Table(data, colWidths=[100,75,75,75,75,75,75], rowHeights=20)
    table.setStyle(TableStyle([

    # t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
    #                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black)]))

        ('FONT',(0,0),(-1,-1), 'Helvetica-Bold', 18),
        ('TEXTCOLOR',(0,0),(-1,-1),colors.white),
        ('BOTTOMPADDING',(0,0),(-1,0),8),
        # set font and color for top row
        ('FONTSIZE',(0,0),(-1,0),18),
        ('TEXTCOLOR',(0,0),(-1,0),colors.cyan),
        # set font size and color for first column
        ('FONTSIZE',(0,1),(0,-1),18),
        ('TEXTCOLOR',(0,1),(0,-1),colors.cyan),
        # set font size and color for second column
        ('FONTSIZE',(1,1),(1,-1),16),
        ('TEXTCOLOR',(1,1),(1,-1),colors.whitesmoke),
        # set font size and color for third and fourth column
        ('FONTSIZE',(2,1),(3,-1),16),
        ('TEXTCOLOR',(2,1),(3,-1),colors.whitesmoke),
        # set font size and color for fifth column
        ('FONTSIZE',(4,1),(4,-1),16),
        ('TEXTCOLOR',(4,1),(4,-1),colors.whitesmoke),
        # ('BACKGROUND',(4,1),(4,-1),bcolor),
        # set font size and color for sixth and seventh columns
        ('FONTSIZE',(5,1),(6,-1),16),
        ('TEXTCOLOR',(5,1),(6,-1),colors.whitesmoke),
        # set font size and color for eighth column
        ('FONTSIZE',(7,1),(7,-1),16),
        ('TEXTCOLOR',(7,1),(7,-1),colors.whitesmoke),
        # ('ALIGN',(1,1), (1,-1),'RIGHT'),
        ('ALIGN',(1,0), (-1,-1),'CENTER'),
        ]))
    w, h = table.wrapOn(c, width, height)
    table.drawOn(c, 10, 310-h)

    c.showPage()
    c.save()

GenerateSlide()

images = convert_from_path('RecruitmentSlide.pdf')
for image in images:
    image.save('RecruitmentSlide.png')


# Convert pdf to png
# def Makepng():
    # images = convert_from_path('RecruitmentSlide.pdf')
    # for image in images:
    #     image.save('RecruitmentSlide.png')

# Define and start the bot
# forv

#Defining a few things
secret_file = json.load(open(cwd+'/bot_config/secrets.json'))
RecBot = commands.Bot(command_prefix='$', case_insensitive=True)#, owner_id=271612318947868673)
RecBot.config_token = secret_file['token']
logging.basicConfig(level=logging.INFO)
RecBot.version = "0.1.0"

@RecBot.event
async def on_ready():
    print(f"-----\nLogged in as: {RecBot.user.name} : {RecBot.user.id}\n-----\nMy current prefix is: $\n-----")
    await RecBot.change_presence(activity=discord.Game(name=f"Hi, my names {RecBot.user.name}.\nUse $ to interact with me!")) # This changes the bots 'activity'
    try:
        with open("OpenSlots.txt") as f: 
            content = "\n".join(f.readlines())
        await ctx.send("```"+'\n' +content+'\n'+"```")
    except:
        await ctx.send("Oops")

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
        # force update
        # Makepng()
        await ctx.send(file=discord.File('RecruitmentSlide.png'))
    except:
        await ctx.send("Could not fetch data. Please try again")

@RecBot.command(name='NeedMembers', aliases=['members', 'nm'])
async def NeedMembers(ctx):
#     """
#     Get list of guilds needing members
#     """
    try:
        with open("OpenSlots.txt") as f: 
            content = "\n".join(f.readlines())
        await ctx.send("```"+'\n' +content+'\n'+"```")
    except:
        await ctx.send("Oops")

@tasks.loop(seconds=60)
async def PostMembers():
    try:
        with open("OpenSlots.txt") as f: 
            content = "\n".join(f.readlines())
        await ctx.send("```"+'\n' +content+'\n'+"```")
    except:
        await ctx.send("Oops")
PostMembers.start()
        
RecBot.run(RecBot.config_token) #Runs our bot