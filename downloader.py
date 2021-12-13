# Requirements
import requests
import settings
import urllib.request
import urllib.error
from colorama import init
from colorama import Style, Fore, Back
from contextlib import suppress
from pathlib import Path
from bs4 import BeautifulSoup

def download_card (txt,set,code,name,artist,scrylink,name2,layout):

	# Make sure numeric code is 3 digits
	if len(code) == 1: code = "00"+code
	elif len(code) == 2: code = "0"+code
	
	# Some sets aren't represented accurately on mtgpics, lets fix it
	set = fix_set_mtgp(set)
	filename = "/" + name + " (" + artist + ") [" + set.upper() + "].jpg"

	# First part of mtgp link, and flip scryfall
	baselink = "https://mtgpics.com/pics/art/"+set+"/"
	flipscry = scrylink.replace("front","back")

	# Which type of card?
	if layout == "transform" or layout == "modal_dfc" or layout == "split":

		# Download front side
		download_front (txt,set,code,name,filename,scrylink)

		# New filename for back side, download back side
		filename = "/" + name2 + " (" + artist + ") [" + set.upper() + "].jpg"
		download_back (txt,set,code,name2,filename,flipscry)

	else: download_front (txt,set,code,name,filename,scrylink)

def download_front (txt,set,code,name,filename,scrylink):
	try:
		# Crawl the mtgpics site to find correct link for mdfc card
		r = requests.get("https://www.mtgpics.com/card?ref="+set+code)
		soup = BeautifulSoup(r.content, "html.parser")
		soup_img = soup.find("img", {"style": "display:block;border:4px black solid;cursor:pointer;"})
		img_src = soup_img['src']
		img_link = img_src.replace("pics/art_th/","")
		mtgp_link = "https://mtgpics.com/pics/art/"+img_link
		
		# Try to download from MTG Pics
		urllib.request.urlretrieve(mtgp_link, settings.f_mtgp + filename)
		print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + name)
	except:
		# Failed so download from scryfall art crop
		print(f"{Fore.RED}MTGP is missing " + name + ", checking Scryfall...")
		try: 
			urllib.request.urlretrieve(scrylink, settings.f_scry + filename)
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + name)
		except:
			txt.write(name+" (https://www.mtgpics.com/card?ref="+set+code+")\n")
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + name)

def download_back (txt,set,code,name,filename,scrylink):
	try:
		# Crawl the mtgpics site to find correct link for mdfc card
		r = requests.get("https://www.mtgpics.com/card?ref="+set+code)
		soup = BeautifulSoup(r.content, "html.parser")
		soup_img = soup.find_all("img", {"style": "display:block;border:4px black solid;cursor:pointer;"})
		img_src = soup_img[1]['src']
		img_link = img_src.replace("pics/art_th/","")
		mtgp_link = "https://mtgpics.com/pics/art/"+img_link
		
		# Try to download flip from MTG Pics
		urllib.request.urlretrieve(mtgp_link, settings.f_mtgp_b + filename)
		print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + name + " (Back)")
	except:
		# Failed so download from scryfall art crop
		print(f"{Fore.RED}MTGP is missing " + name + " (Back), checking Scryfall...")
		try: 
			urllib.request.urlretrieve(flipscry, settings.f_scry_b + filename)
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + name + " (Back)")
		except:
			txt.write(name+" (https://www.mtgpics.com/card?ref="+set+code+")\n")
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + name + " (Back)")

# Beta feature, needs additional work
def download_cards (txt, json):
	
	mtgp = 0
	mtgp_b = 0
	
	for card in json:
		
		# Base variables
		set = card['set']
		card_num = card['collector_number']
		artist = card['artist']
		flipname = ""
		set = fix_set_mtgp(set)
		
		# Is this mdfc?
		if 'card_faces' in card:
			flipname = card['card_faces'][1]['name']
			art_crop = card['card_faces'][0]['image_uris']['art_crop']
			card_name = card['card_faces'][0]['name']
		else:
			art_crop = card['image_uris']['art_crop']
			card_name = card['name']
			mtgp_b = 1
		
		baselink = "https://mtgpics.com/pics/art/"+set+"/"
		
		# Has MTGPic art been found yet?
		if mtgp != 1:
			try:
				try:
					# Crawl the mtgpics site to find correct link for mdfc card
					r = requests.get("https://www.mtgpics.com/card?ref="+set+card_num)
					soup = BeautifulSoup(r.content, "html.parser")
					soup_img = soup.find("img", {"style": "display:block;border:4px black solid;cursor:pointer;"})
					img_src = soup_img['src']
					img_link = img_src.replace("pics/art_th/","")
					mtgp_link = "https://mtgpics.com/pics/art/"+img_link
				except:
					mtgp_link = "https://mtgpics.com/pics/art/"+set+"/"+card_num+".jpg"
				# Try to download from MTG Pics
				urllib.request.urlretrieve(mtgp_link, settings.f_mtgp + "/" + card_name + " (" + artist + ").jpg")
				print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + card_name)
				mtgp = 1
			except: mtgp = 0
		
		# Has MTGPic art been found for back?
		if mtgp_b != 1:
			try:
				# Crawl the mtgpics site to find correct link for mdfc card
				r = requests.get("https://www.mtgpics.com/card?ref="+set+card_num)
				soup = BeautifulSoup(r.content, "html.parser")
				soup_img = soup.find_all("img", {"style": "display:block;border:4px black solid;cursor:pointer;"})
				img_src = soup_img[1]['src']
				img_link = img_src.replace("pics/art_th/","")
				mtgp_link = "https://mtgpics.com/pics/art/"+img_link
				
				# Try to download flip from MTG Pics
				urllib.request.urlretrieve(mtgp_link, settings.f_mtgp_b + "/" + flipname + " (" + artist + ").jpg")
				print(f"{Fore.GREEN}SUCCESS MTGP: {Style.RESET_ALL}" + flipname + " (Back)")
				mtgp_b = 1
			except: mtgp_b = 0
	
	card = json[0]
	
	# Base variables
	set = card['set']
	card_num = card['collector_number']
	artist = card['artist']
	flipname = ""
	
	# Is this mdfc?
	if 'card_faces' in card:
		flipname = card['card_faces'][1]['name']
		art_crop = card['card_faces'][0]['image_uris']['art_crop']
		card_name = card['card_faces'][0]['name']
		flipscry = json[0]['card_faces'][1]['image_uris']['art_crop']
	else:
		art_crop = card['image_uris']['art_crop']
		card_name = card['name']
		mtgp_b = 1
	
	# Did MTGP fail all?
	if mtgp == 0:
		print(f"{Fore.RED}FAILED MTGP: {Style.RESET_ALL}" + card_name + ", trying scryfall...")
		try: 
			urllib.request.urlretrieve(art_crop, settings.f_scry + "/" + card_name + " (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + card_name)
		except:
			txt.write(name+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + card_name)
	
	# Did MTGP fail all backs?
	if mtgp_b == 0:
		print(f"{Fore.RED}FAILED MTGP: {Style.RESET_ALL}" + flipname + " (Back), trying scryfall...")
		try: 
			urllib.request.urlretrieve(flipscry, settings.f_scry_b + "/" + flipname + " (" + artist + ").jpg")
			print(f"{Fore.GREEN}SUCCESS SCRY: {Style.RESET_ALL}" + flipname + " (Back)")
		except:
			txt.write(flipname+'\n')
			print(f"{Fore.RED}FAILED ALL: {Style.RESET_ALL}" + flipname + " (Back)")

def fix_set_mtgp (set):
	if set == "arb": return("alr")
	if set == "mp2": return("aki")
	if set == "atq": return("ant")
	if set == "apc": return("apo")
	if set == "arn": return("ara")
	if set == "e01": return("anb")
	if set == "anb": return("an2")
	if set == "bok": return("bek")
	if set == "csp": return("col")
	if set == "c13": return("13c")
	if set == "c14": return("14c")
	if set == "c15": return("15c")
	if set == "c16": return("16c")
	if set == "c17": return("17c")
	if set == "cn2": return("2cn")
	if set == "dst": return("drs")
	if set == "dpa": return("dop")
	if set == "e02": return("dop")
	if set == "fem": return("fal")
	if set == "5dn": return("fda")
	if set == "v17": return("ftr")
	if set == "gpt": return("gui")
	if set == "hml": return("hom")
	if set == "mps": return("kli")
	if set == "lgn": return("lgi")
	if set == "lrw": return("lor")
	if set == "m10": return("10m")
	if set == "m11": return("11m")
	if set == "m12": return("12m")
	if set == "m13": return("13m")
	if set == "m14": return("14m")
	if set == "m15": return("15m")
	if set == "a25": return("25m")
	if set == "mmq": return("mer")
	if set == "mm2": return("mmb")
	if set == "mm3": return("mmc")
	if set == "hop": return("pch")
	if set == "pc2": return("2pc")
	if set == "pls": return("pla")
	if set == "p02": return("psa")
	if set == "pd2": return("fir")
	if set == "pd3": return("gra")
	if set == "pcy": return("pro")
	if set == "3ed": return("rev")
	if set == "sok": return("sak")
	if set == "scg": return("sco")
	if set == "shm": return("sha")
	if set == "ala": return("soa")
	if set == "sta": return("stm")
	if set == "sth": return("str")
	if set == "tmp": return("tem")
	if set == "drk": return("dar")
	if set == "puma": return("uma")
	if set == "uma": return("ulm")
	if set == "ugl": return("ung")
	if set == "wth": return("wea")
	if set == "exp": return("zex")
	else: return(set)