#!/usr/bin/python
import interactions
import discord
import os
import requests
import json
import random

# Prepare environment
# import asyncpg
from discord.ext import tasks
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
from update_gnum import update_gnum

from interactions.ext.get import get


#

# Discord login


def update_all_guild():
    # try:
    f = open('OpenSlots.txt', "w")
    f.close()

    # Discord interactions aka slash commands
    # bot = interactions.Client(token='DISCORD_TOKEN')

    # Fetch configuration variables
    with open('config.yml') as file:
        config = yaml.safe_load(file)

    # Fetch guild data from game. From the raw data populate guilds

    # Make the connection
    creds = settings(config['CredName'], config['CredPass'], config['CredNum'], config['CredLet'])
    client = SWGOHhelp(creds)

    # Fetch the data
    guilds = []
    NumPass = 1
    # f = open('OpenSlots.txt', "w")
    # f.close()

    # Clear OpenSlots file because Replit doesnt like the close function

    w = open('OpenSlots.txt', "w")
    w.write("")
    w.close()

    f = open('OpenSlots.txt', 'a')

    # f.write('Name\tMembers\tGP\n')
    f.write('Name'.ljust(15) + 'Members'.rjust(7) + 'GP'.rjust(8) + '\n')
    f.close()
    for allycode in config['allycodes']:
        def GetData():
            try:
                print('Trying to get guild data', NumPass, '/14')
                response = client.get_data('guild', allycode)
                # print(response)
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
            'GGp': guildinfo['gp'],
            'GName': NameProcessed,
            'GMembers': guildinfo['members'],
            'GRaid': guildinfo['raid'],
            'AllyCode': allycode,
        })

        # Generate text file to list guilds with membership below 50

        f = open('OpenSlots.txt', "a")
        if guildinfo['members'] < 50: f.write(
            NameProcessed.ljust(15) + str(guildinfo['members']).rjust(5) + str(round(guildinfo['gp'] / 1000000)).rjust(
                10) + '\n')
        f.close()

        print('Success!')
        NumPass += 1
    # Add time marker to OpenSlots
    now = datetime.datetime.now() - datetime.timedelta(hours=5)
    t = open('OpenSlots.txt', "a")
    t.write("Guilds not at Capacity"+'\n'+"Updated: " + now.strftime("%Y-%m-%d %H:%M:%S" + " CST " + '\n'))
    t.close()

    # populate Canvas

    # Create the Canvas object
    c = canvas.Canvas(config['RSFilename'])
    width = 740
    height = 360
    c.setPageSize((width, height))
    c.setTitle(config['RSTitle'])

    c.drawImage('RPBackgroun.jpeg', 0, 0, width=width, height=height)
    c.drawImage('Shard-Character-Ki-Adi-Mundi.png', 492, 300, width=30, height=30)
    c.drawImage('Shard-Character-Wat_Tambor.png', 578, 300, width=30, height=30)
    # add the title to the image
    c.setFont(config['Font'], config['FontSize'])
    c.setFillColor(colors.whitesmoke)
    docTitle = config['RSDocumentTitle']
    docTitle = regex.sub(r'\?\?', "\u00F8", config['RSDocumentTitle'])
    # print(docTitle)
    c.drawCentredString(width / 2, 330, docTitle)

    # populate data for the table

    # create first row of table
    data = [['', 'GP', 'DSTB', 'LSTB', 'CPit', ' ', ' ', 'GM']]
    # create the rest of the rows
    for guild in guilds:
        # modify appearance and content of items in guilds
        GPRounded = str(round(guild['GGp'] / 1000000))
        DSTB = config['DSTB'][guild['GName']]
        LSTB = config['LSTB'][guild['GName']]
        CPIT = config['CPIT'][guild['GName']]
        KAM = config['KAM'][guild['GName']]
        WAT = config['WAT'][guild['GName']]
        # create table row
        data.append([guild['GName'], GPRounded, DSTB, LSTB, CPIT, KAM, WAT, guild['GMembers']])

    # create Table object based on data and add to image
    table = Table(data, colWidths=[130, 82, 82, 82, 82, 82], rowHeights=20)
    table.setStyle(TableStyle([
        # set font for table
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 18),
        # create some space between first row and rest of table
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        # First column font size and color
        ('FONTSIZE', (0, 0), (0, -1), 18),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.cyan),
        # First row font size and color
        ('FONTSIZE', (0, 0), (0, -1), 18),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.cyan),
        # The rest
        ('FONTSIZE', (1, 1), (-1, -1), 16),
        ('TEXTCOLOR', (1, 1), (-1, -1), colors.whitesmoke),
        # Apply centering to all columns but the first
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))

    # Print the table
    table.wrapOn(c, width, height)
    table.drawOn(c, 10, 10)

    # Create the pdf
    c.save()

    pages = convert_from_path('RecruitmentSlide.pdf', 500)
    for page in pages:
        page.save('RecruitmentSlide.png', 'PNG')


# def update_all_test():
# try:
#  update_all()
#  else:
#  raise ValueError

# try:
#   update_all_test()
# except ValueError:
# update_all()

# discord event handling
# disclient = discord.Client()
bot = interactions.Client(token=os.getenv('DISCORD_TOKEN'))


@bot.event
async def on_ready():
    # We can use the client "me" attribute to get information about the bot.
    print(f"We're online! We've logged in as {bot.me.name}.")

    # We're also able to use property methods to gather additional data.
    print(f"Our latency is {round(bot.latency)} ms.")
    # myLoop.start
    keep_alive()


bot.load('interactions.ext.files')


# bot.load('interactions-ext-files')
# bot.load("interactions.ext.enhanced")
@bot.command(
    name="rslide",
    description="Posts Recruitment Slide for guild"
)
async def rslide(ctx):
    await ctx.send("Posting Recruitment Slide")

    channel = await get(bot, interactions.Channel, channel_id=991120479026946068)
    #channel_rec = await get(bot, interactions.Channel, channel_id=938273738191958036)
    img = interactions.File('RecruitmentSlide.png')
    await channel.send(files=img)
    #await channel_rec.send(files=img)
    await ctx.edit("Recruitment Slide Posted")


@bot.command(
    name="gnum",
    description="Posts Recruitment Numbers"
)
async def gnum(ctx):

    await ctx.send("Posting Recruitment Numbers")
    channel = await get(bot, interactions.Channel, channel_id=991120479026946068)
    #channel_rec = await get(bot, interactions.Channel, channel_id=938273738191958036)
    with open("OpenSlots.txt") as f: content = "\n".join(f.readlines())
    await channel.send("```" + '\n' + content + '\n' + "```")
    #await channel_rec.send("```" + '\n' + content + '\n' + "```")
    await ctx.edit("Recruitment Numbers Posted")


@bot.command(
    name="update_all",
    description="Updates Recruitment Slide and Guild Numbers"
)
async def update_all(ctx):
  try:
      await ctx.send("Updating Recruitment Slide and Guild Numbers")
      update_all_guild()
      await ctx.edit("Recruitment Slide and Guild Numbers Updated")
  except:
      await ctx.edit("Error in Update. Please rerun command.")


@bot.command(
    name="update_num",
    description="Updates Guild Numbers"
)
async def update_num(ctx):
  try:
      await ctx.send("Updating Guild Numbers")
      update_gnum()
      await ctx.edit("Guild Numbers Updated")
  except:
      await ctx.edit("Error in Update. Please rerun command.")


@bot.command(
    name="help",
    description="Lists Commands Recognized by Phantom-Recruit-Bot"
)
async def help(ctx):
    await ctx.send(
        "Commands Recognized by Phantom-Officer-Bot:" + '\n' + "/updateall- starts the bot and pulls all fresh data" + '\n' + "/updatenum- updates the guild numbers for the shortlined text" + '\n' + "/rslide- post the recruitment slide" + '\n' + "/gnum- post guilds numbers who are not at capacity" + '\n' + "/pushup- pushes the updated numbers and slide to the bot channel")


@bot.command(
    name="pushup",
    description="Pushes Recruitment Slide and Guild Numbers to Bot channel"
)
async def pushup(ctx):
    await ctx.send("Pushing to Bot channel")
    channel = await get(bot, interactions.Channel, channel_id=991120479026946068)
    #channel_rec = await get(bot, interactions.Channel, channel_id=938273738191958036)
    with open("OpenSlots.txt") as f: content = "\n".join(f.readlines())
    await channel.send("```" + '\n' + content + '\n' + "```")
    #await channel_rec.send("```" + '\n' + content + '\n' + "```")
    img = interactions.File('RecruitmentSlide.png')
    await channel.send(files=img)
    #img = interactions.File('RecruitmentSlide.png')
    #await channel_rec.send(files=img)
    await ctx.edit(content="Pushed")


@tasks.loop(hours=1)
async def TestLoop1():
    print('Updating...')
    #  await disclient.mychannel.send("Updating guild data..")
    # update_all()
    try:
        update_all_guild()
    except:
        update_all_guild()


TestLoop1.start()


@tasks.loop(hours=2)
async def testloop():
    print('Posting...')
    #  await disclient.mychannel.send("Updating guild data..")
    # update_all()
    channel = await get(bot, interactions.Channel, channel_id=991120479026946068)
    #channel_rec = await get(bot, interactions.Channel, channel_id=938273738191958036)
    with open("OpenSlots.txt") as f: content = "\n".join(f.readlines())
    await channel.send("```" + '\n' + content + '\n' + "```")
    #await channel_rec.send("```" + '\n' + content + '\n' + "```")
    img = interactions.File('RecruitmentSlide.png')
    await channel.send(files=img)
    #img = interactions.File('RecruitmentSlide.png')
    #await channel_rec.send(files=img)
    print('Posted')


@testloop.before_loop
async def before_testloop():
    await bot.wait_until_ready()
    channel = await get(bot, interactions.Channel, channel_id=991120479026946068)
    #channel_rec = await get(bot, interactions.Channel, channel_id=938273738191958036)


testloop.start()
# disclient.run(os.getenv('DISCORD_TOKEN'))
bot.start()