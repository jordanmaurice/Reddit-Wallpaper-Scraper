import praw
import prawcore
import logging
from PIL import Image
from PIL import ImageFile
import requests
from io import BytesIO
import urllib
import socket
import os
import errno


def getsizes(uri):
    # get file size and image size (None if not known)
	try:
		file = urllib.request.urlopen(uri)
	except urllib.error.HTTPError as e:
		logging.info(uri,e.code)
	except urllib.error.URLError as e:
	    logging.info(uri,'URLError')
	except socket.error as error:
		logging.info(uri,'socket error')
	else:
	    size = file.headers.get("content-length")
	    if size: size = int(size)
	    p = ImageFile.Parser()
	    while 1:
	        data = file.read(1024)
	        if not data:
	            break
	        p.feed(data)
	        if p.image:
	            return size, p.image.size
	            break
	    file.close()
	    return size, None

def sizeSplit(size):

	if size is not None:
		dimensionString = size[1]

		if dimensionString is not None:
			if dimensionString[0] >= desiredWidth and dimensionString[1] >= desiredHeight:
				desiredRatio = desiredWidth/desiredHeight
				currentRatio = dimensionString[0]/dimensionString[1]
				if(desiredRatio == currentRatio):
					print("\n Image found: " + str(dimensionString[0]) +"x"+str(dimensionString[1]))
					return True
	return False

def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except Exception as e:
        print("Oops, it appears that the subreddit " + sub + " does not exist")
        logging.info(e)
        exists= False
    return exists

def checkURL(url):
	try:
	    conn = urllib.request.urlopen(url)
	except urllib.error.HTTPError as e:
	    # Return code error (e.g. 404, 501, ...)
	    logging.info(url,e.code)
	except urllib.error.URLError as e:
	    # Not an HTTP-specific error (e.g. connection refused)
	    logging.info(url,URLError)
	else:
	    # 200 -- link worked!
	    extensions = ['jpg', 'png', 'jpeg'];
	    title = url.split("/")[-1]
	    if('.' in title):
	    	extension = title.split('.')[-1]
	    	if(extension in extensions):
	    		print("File name will be ",title)
	    		print("URL of download is: ",url)
	    		img_obj = requests.get(url)
	    		img = Image.open(BytesIO(img_obj.content))
	    		directory = "./reddit-wallpapers/"
	    		if not os.path.exists(directory):
    				os.makedirs(directory)
    			else:
	    			img.save(directory+title,img.format)


def getResolution():
	resolution = input("Please input your resolution: ex(1920x1080) ")
	resolution = resolution.lower()
	if 'x' in resolution:
		resolutionList = resolution.split('x')
		try:
			global desiredWidth 
			desiredWidth = int(resolutionList[0])
			global desiredHeight 
			desiredHeight = int(resolutionList[1])
		except ValueError:
			print("Invalid input, resolution should be ####x####")
			getResolution()
	else:
		print("Invalid input, resolution should be ####x####")
		getResolution()


reddit = praw.Reddit(client_id='UFLKvfKkEXNfbw',
                     client_secret='Nb0vWF026Rbny9MCf68S0pfVwHg',
                     user_agent='wallpaper-download')
desiredWidth = 0
desiredHeight = 0
getResolution()
userSub = input("Please enter what subreddit(s) to search, separated by commas: ")
subredditList = userSub.split(',')

for subreddit in subredditList:
	if(sub_exists(subreddit)):
		print("Searching subreddit: " + subreddit + " for wallpapers that are: "+str(desiredWidth)+"x"+str(desiredHeight))
		for submission in reddit.subreddit(subreddit).top(limit=1000):
			title = submission.url.split("/")[-1]
			if('.' not in title):
				submission.url = submission.url+'.png'
				size = getsizes(submission.url)
				if(sizeSplit(size)):
					checkURL(submission.url)
			else:
				size = getsizes(submission.url)
				if(sizeSplit(size)):
					checkURL(submission.url)

print("Wallpapers have completed downloading")
