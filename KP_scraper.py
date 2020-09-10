# Made by Mihajlo Jankovic - 2020 <jankovic.mihajlo99@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it.
# Since I am currently the first year student, I have been working on this 
# project for the purpose of practice and also for fun.
# 
# Thank you for visiting and using!
# 
# Enjoy!

import requests,bs4,re,random,webbrowser,time

def is_num(num): # Check if char is num
	if(ord(num) >= ord('0') and ord(num) <= ord('9')): return True
	return False

def convert_to_num(s): # Convert price from str to int
	i = 0
	num = 0
	if(not is_num(s[i])): return (num,'Kontakt')
	
	while(i < len(s) and ord(s[i]) != ' ' and ord(s[i]) != 160): #160 = Unicode Character (NO-BREAK SPACE)
		if(s[i] == '.'):
			i += 1
			continue
		
		elif(s[i] == ','): return (num,'€')
		
		digit = ord(s[i]) - ord('0')
		num = num * 10 + digit
		i += 1
	
	return (num,'din')

def get_proxy(): # Scraping IP/Port from https://www.sslproxies.org/ (Free proxy list)
	url = 'https://www.sslproxies.org/'
	req = requests.get(url)
	
	soup = bs4.BeautifulSoup(req.content, features = 'html.parser')
	ip_list = soup.findAll('td')[0::8]
	port_list = soup.findAll('td')[1::8]
	
	regex_port = re.compile(r'^[0-9]')
	regex_ip = re.compile(r'^[0-9]*[.]')
	
	proxy_list = []
	for i in range(len(ip_list)):
		if(regex_ip.match(ip_list[i].text) and regex_port.match(port_list[i].text)): 
			proxy = ip_list[i].text + ':' + port_list[i].text
			proxy_dict = dict()
			proxy_dict['https'] = proxy
			proxy_list.append(proxy_dict)
			
		else: break
	
	return proxy_list

def proxy_request(request_type, url, **kwargs): # Send a request to the targeted site
	print('Proxy IP/Port - trying to connect...')
	for proxy in proxy_list:
		try:
			print(proxy)
			req = requests.request(request_type, url, proxies = proxy, timeout = 1, **kwargs)
			return req,proxy
			
		except:
			pass
		
	return False
	
proxy_list = get_proxy()

search = input('search (use + instead of SPACEBAR): ')
link = 'https://www.kupujemprodajem.com/search.php?action=list&data%5Bpage%5D=1&data%5Bprev_keywords%5D=tastatura&data%5Border%5D=relevance&submit%5Bsearch%5D=Tra%C5%BEi&dummy=name&data%5Bkeywords%5D='+search

req,valid_proxy = proxy_request('get', link)

if(not req): print('Failed to access...\n')
print('\nIP successfully connected.\n')
print('Valid proxy = ', end = '')
print(valid_proxy)

soup =  bs4.BeautifulSoup(req.content, features = 'html.parser')

h1_list = soup.select('h1')

flag = 1
for h1 in h1_list:
	h1 = h1.text.strip()
	print(h1)
	if(h1 == 'Vama je blokiran pristup portalu!'): 
		print('\nNeuspelo povezianje (blokiran pristup)...')
		flag = 0
		break

if(flag): # Main scraper
	ads = []
	kp_link = 'https://www.kupujemprodajem.com'
	ad_list_container = soup.findAll("div",{"id":"adListContainer"})
	ad_list = ad_list_container[0].findAll("div",{"class":"clearfix"})
	
	for i in range(1,len(ad_list),2):
		name = ad_list[i].find('img')
		name = name.get('alt', '')
		name = re.sub(' +', ' ', name)
		
		price = ad_list[i].find('span',{'class':'adPrice'})
		price = price.text.strip()
		price_tuple = convert_to_num(price)
		price = price_tuple[0]
		if(price != 0): price_str = str(price_tuple[0]) + ' ' + price_tuple[1]
		else: price_str = price_tuple[1]
		
		link = ad_list[i].find('a')
		link = link.get('href', '')
		link = kp_link + link
		
		req = requests.request('get', link, proxies = valid_proxy)
		soup =  bs4.BeautifulSoup(req.content, features = 'html.parser', from_encoding="iso-8859-1")
		
		if(soup.find("div",{"class":"thumb-up"})):
			like_num = int(soup.find("div",{"class":"thumb-up"}).find("span").text)
			dislike_num = int(soup.find("div",{"class":"thumb-down"}).find("span").text)
		
		else:
			like_num = 0
			dislike_num = 0
		
		ads.append((name,price_str,price,like_num,dislike_num,link))
	
	#Sorting
	print('Sort ads:')
	print('1) Sort by price')
	print('2) Sort by number of likes')
	print('3) Sort by number of dislikes')
	j = int(input('Enter the number you want to sort by: ')) + 1
	print('\n')
	
	sorted_list = []
	ind = 0
	while(len(ads)):
		max_index = 0
		for i in range(1,len(ads)):
			if(ads[i][j] > ads[max_index][j]): max_index = i
		
		ad_tuple = ads.pop(max_index)
		sorted_list.append(ad_tuple)
	
	for i in range(len(sorted_list)):
		print('------------ Ad ' + str(i+1) + ' ------------')
		print('Ad name: ' + str(sorted_list[i][0]))
		print('Product price: ' + str(sorted_list[i][1]))
		print('Likes/Dislikes: ' + str(sorted_list[i][3]) + '/' + str(sorted_list[i][4]))
		
	flag = int(input('\nEnter Ad number to open Ad in browser or 0 to exit: ')) - 1
	while(flag != -1):
		webbrowser.open(sorted_list[flag][5], new=2)
		time.sleep(0.5)
		flag = int(input('\nEnter Ad number to open Ad in browser or 0 to exit: ')) - 1
	
	print('Program closed...')
