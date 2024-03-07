import pandas as pd 
import requests 
from bs4 import BeautifulSoup

fishURL = "https://dredge.fandom.com/wiki/Fish"
aberrationURL = "https://dredge.fandom.com/wiki/Aberrations"

# Get the first table's text data, setting the Numbers column as the index.
fishFrame = pd.read_html(fishURL, index_col='Number')[0]
aberrationFrame = pd.read_html(aberrationURL)[0]
# Pandas issue. Set index manually for aberration table...
aberrationFrame.set_index('Number', inplace=True)

# Cast the image and type columns to string. It reads it in as NaN and assumes it's float.
fishFrame['Image'] = fishFrame['Image'].astype('str')
fishFrame['Type'] = fishFrame['Type'].astype('str')
aberrationFrame['Image'] = aberrationFrame['Image'].astype('str')
aberrationFrame['Type'] = aberrationFrame['Type'].astype('str')

### BS4 USAGE ### 

# Get the pages 
fishPage = requests.get(fishURL)
aberrationPage = requests.get(aberrationURL)
# Parse the page conent with an HTML parser
fishContent = BeautifulSoup(fishPage.content, "html.parser")
aberrationContent = BeautifulSoup(aberrationPage.content, "html.parser")
# Get the tabular data of the fishes
fishTable = fishContent.find('table', class_='article-table')
aberrationTable = aberrationContent.find('table', class_='article-table')

# Get the entry for the fish
fishEntries = fishTable.find_all('tr') # Each fish entry tablerow 
for idx, fishEntry in enumerate(fishEntries): # Each datapoint in the row 
    # Get the images from fishEntry. 
    fishImageLinks = fishEntry.find_all('img')
    for image in fishImageLinks: 
        # Get each image's source link. 
        imageLink = image.get('data-src')
        if ("TypeBadge" in imageLink): 
            fishFrame.at[idx, 'Type'] = str(imageLink) 
        else:
            fishFrame.at[idx, 'Image'] = str(imageLink) 

# Replace the Aberration column with our own data to add separators between Abberations
for fishIndex, fishEntry in enumerate(fishEntries):
    fishDataPoints = fishEntry.find_all('td')
    count = 1
    for idx, fishDataPoint in enumerate(fishDataPoints):
        if (idx % 6 == 0 and idx != 0):
            aberrationLinks = fishDataPoint.find_all('a')
            if len(aberrationLinks) == 0:
                aberrationList = "N/A"
            else:
                aberrationList = ""
            for horrorIndex, aberrationLink in enumerate(aberrationLinks, start=1):
                aberrationList += aberrationLink.get('title')
                if (len(aberrationLinks) > 1 and horrorIndex != len(aberrationLinks)):
                    aberrationList += ", "
            # Add it to the dataframe, replacing the data there
            fishFrame.at[fishIndex, 'Aberrations'] = aberrationList


# Get the entry for the aberration
aberrationEntries = aberrationTable.find_all('tr') # Each aberration entry tablerow 
for idx, aberrationEntry in enumerate(aberrationEntries, start=78): # Each datapoint in the row 
    # Get the images from aberrationEntry. 
    aberrationImageLinks = aberrationEntry.find_all('img')
    for image in aberrationImageLinks: 
        # Get each image's source link. 
        imageLink = image.get('data-src')
        if ("TypeBadge" in imageLink): 
            aberrationFrame.at[idx, 'Type'] = str(imageLink) 
        else:
            aberrationFrame.at[idx, 'Image'] = str(imageLink) 
    
# Write the JSON 
fishJSON = open("dredgeFishData.json", 'w')
fishJSON.write(fishFrame.to_json())
fishJSON.close()
aberrationJSON = open("dredgeAberrationData.json", 'w')
aberrationJSON.write(aberrationFrame.to_json())
aberrationJSON.close()
