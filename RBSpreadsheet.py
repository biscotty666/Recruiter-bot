from pprint import pprint
from googleapiclient.discovery import build
from google.oauth2 import service_account

keyfile = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
        keyfile, scopes=SCOPES)


# Create the service and sheet object
SpreadsheetsID = '14s5-_5BDiaYrzSqVeKX4vkkn4iBy8qxRm2P2ugFIUn4'
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

result = sheet.values().get(spreadsheetId=SpreadsheetsID,
                            range="Alliance!a1:b").execute()
GuildList = result.get('values', [])

guilds = []

# l1 = [[1,2],[3,4],[5,[6,7]]]
# d1={x[0]:x[1] for x in l1}
# print(d1)#Output:{1: 2, 3: 4, 5: [6, 7]}

for guild in GuildList:
    name = guild[0]
    result = sheet.values().get(spreadsheetId=SpreadsheetsID,
                            range=str(name)+"!a1:b7").execute()
    GuildStats = result.get('values', {})
    GSD = {x[0]:x[1] for x in GuildStats}
    
    DSTB = GSD['DSTB']
    LSTB = GSD['LSTB']
    CPIT = GSD['CPIT']
    WAT = GSD['WAT']
    KAM = GSD['KAM']
   
    pprint(DSTB)
    