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

#get file size and image size (None if not known)
def get_size(uri):
	try:
		file = urllib.request.urlopen(uri)
	except urllib.error.HTTPError as e:
		logging.info(uri,e.code)
	except urllib.error.URLError as e:
	    logging.info(uri,'URL Error')
	except socket.error as error:
		logging.info(uri,'Socket Error')
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

#Checks the size of a given image to determine if it matches the user defined ratio.  
def size_split(size):
	if size is not None:
		dimensionString = size[1]

		if dimensionString is not None:
			if dimensionString[0] >= desiredWidth and dimensionString[1] >= desiredHeight:
				desiredRatio = desiredWidth/desiredHeight
				currentRatio = dimensionString[0]/dimensionString[1]
				if(desiredRatio == currentRatio):
					print("\nImage found: {}x{}".format(str(dimensionString[0]), str(dimensionString[1])))
					return True
	return False

#Checks using the praw instance whether a subreddit exists
def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except Exception as e:
        print("Oops, it appears that the subreddit r/{} does not exist".format(sub))
        logging.info(e)
        exists= False
    return exists


#Determine if a URL from reddit is valid
def check_url(url):
	try:
	    conn = urllib.request.urlopen(url)
	except urllib.error.HTTPError as e:
	    logging.info(url,e.code)
	except urllib.error.URLError as e:
	    logging.info(url,URLError)
	else:
	    # 200 -- link worked!
	    download_image(url)

#Save image to directory
def download_image(url):
	extensions = ['jpg', 'png', 'jpeg']
	title = url.split("/")[-1]
	try:
		if('.' in title):
			extension = title.split('.')[-1]
			if(extension in extensions):
				print("File name will be {}".format(title))
				print("URL of download is: {} ".format(url))
				img_obj = requests.get(url)
				img = Image.open(BytesIO(img_obj.content))
				directory = "./reddit-wallpapers/"
		   		
				if not os.path.exists(directory):
					os.makedirs(directory)
				else:
					img.save(directory + title, img.format)
	except:
		print("Unexpected error downloading image, moving on")
		pass

#Gets input from user about what their resolution is
def get_resolution():
	resolution_list = ['3840x2160','2560x1440','1920x1080', '1440x900', '1600x900']
	resolution = input("Please choose a resolution: \n3840x2160\n2560x1440\n1920x1080\n1440x900\n1600x900\nChosen Resolution: ")
	resolution = resolution.lower()

	if resolution in resolution_list:
		resolution_split = resolution.split('x')
		global desiredWidth 
		global desiredHeight 
		desiredWidth = int(resolution_split[0])
		desiredHeight = int(resolution_split[1])
	else:
		print("Invalid input, resolution should be ####x####")
		get_resolution()


#Reddit praw instance
reddit = praw.Reddit(client_id='CLIENT_ID',
                     client_secret='CLIENT_SECRET',
                     user_agent='USER_AGENT')
desiredWidth = 0
desiredHeight = 0

get_resolution()

userSub = input("Please enter what subreddit(s) to search, separated by commas: ")
subredditList = userSub.split(',')

for subreddit in subredditList:
	if(sub_exists(subreddit)):
		print("Searching subreddit: {} for wallpapers that are: {}x{}".format(subreddit,str(desiredWidth), str(desiredHeight)))
		
		#Loop through top 1000 submissions to the subreddit.
		for submission in reddit.subreddit(subreddit).top(limit=1000):
			#Title grabs the end of the URL in order to create a file name 
			title = submission.url.split("/")[-1]
			#if the file has an extension in the URL, use that, otherwise add .png 
			if('.' not in title):
				submission.url = submission.url+'.png'
				size = get_size(submission.url)
				if(size_split(size)):
					check_url(submission.url)
			else:
				size = get_size(submission.url)
				if(size_split(size)):
					check_url(submission.url)

print("Wallpapers have completed downloading")