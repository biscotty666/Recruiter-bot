def GetSSData():

    from pprint import pprint
    from google.oauth2 import service_account
    from googleapiclient.discovery import build


    keyfile = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    creds = None
    creds = service_account.Credentials.from_service_account_file(
        keyfile, scopes=SCOPES)


    # Create the service and sheet object
    SpreadsheetsID = '14s5-_5BDiaYrzSqVeKX4vkkn4iBy8qxRm2P2ugFIUn4'
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Get the guild names from the Alliance sheet and store in GuildList
    result = sheet.values().get(spreadsheetId=SpreadsheetsID,
                            range="Alliance!a1:b").execute()
    GuildList = result.get('values', [])

    # Initialize variables
    guilds = []
    GuildListLine = []

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



