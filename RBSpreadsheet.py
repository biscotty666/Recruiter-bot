from pprint import pprint

def MakeSheet():
    from pprint import pprint
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    import yaml

    keyfile = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_file(
        keyfile, scopes=SCOPES)

    # Create the service and sheet object
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return sheet

def GetNames():
    # Get the guild names from the Alliance sheet and store in GuildList
    # Load configuration variables
    import yaml
    with open('config.yml') as file :
        config = yaml.safe_load(file)
    SpreadsheetsID = config['SpreadsheetsID']
    sheet = MakeSheet()
    result = sheet.values().get(spreadsheetId=SpreadsheetsID,
                            range="Alliance!a1:b").execute()
    GuildNameList = result.get('values', [])
    return GuildNameList

def GetACs():
    # Get the guild ally codes from the Alliance sheet and store in GuildList
    ACList = []
    # Load configuration variables
    import yaml

    with open('config.yml') as file :
        config = yaml.safe_load(file)
    SpreadsheetsID = config['SpreadsheetsID']

    names = GetNames()
    for alliance in names:
        name = alliance[0]
        sheet = MakeSheet()
        result = sheet.values().get(spreadsheetId=SpreadsheetsID,
                                    range=str(name)+"!b2").execute()
        ResultValues = result.get('values', {})
        ACList.append(ResultValues[0][0])
    return ACList


def GetSSData():

    # from pprint import pprint
    # from google.oauth2 import service_account
    # from googleapiclient.discovery import build


    # keyfile = 'keys.json'
    # SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # creds = None
    # creds = service_account.Credentials.from_service_account_file(
    #     keyfile, scopes=SCOPES)


    # # Create the service and sheet object
    # SpreadsheetsID = '14s5-_5BDiaYrzSqVeKX4vkkn4iBy8qxRm2P2ugFIUn4'
    # service = build('sheets', 'v4', credentials=creds)
    # sheet = service.spreadsheets()
    sheet = MakeSheet()
    # Get the guild names from the Alliance sheet and store in GuildList
    # result = sheet.values().get(spreadsheetId=SpreadsheetsID,
    #                         range="Alliance!a1:b").execute()
    # GuildList = result.get('values', [])
    GuildList = GetNames()

    # Initialize variables
    guilds = []
    GuildListLine = []

    import yaml
    with open('config.yml') as file :
        config = yaml.safe_load(file)
    SpreadsheetsID = config['SpreadsheetsID']

    # Go through each guild and add stats to guilds variable
    for guild in GuildList:
        name = guild[0]
        # Get all stats from guild Sheet and store in GuildStats
        result = sheet.values().get(spreadsheetId=SpreadsheetsID,
                                    range=str(name)+"!a1:b7").execute()
        GuildStats = result.get('values', {})

        # GuildStats are a list of lists, but we need a list of
        # dictionaries so we create GuildListLine for the list of
        # dictionaries which we can then append to guilds
        for line in GuildStats:
            item = iter(line)
            ds = dict(zip(item, item))
            GuildListLine.append(ds)

        # Add placeholders for live data generated in main.py
        GuildListLine.append({"GP": 0})
        GuildListLine.append({"GM": 0})
        guilds.append(GuildListLine)
        GuildListLine = []

    return guilds

guilds = GetSSData()
pprint(guilds)