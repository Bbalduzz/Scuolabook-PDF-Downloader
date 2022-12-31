import requests, os, shutil, json
from natsort import natsorted
from PIL import Image
from bs4 import BeautifulSoup
import re, json
import fitz
import math

raw_url = input('Enter the book url: \n')

with open('cookies.txt', 'r') as f: auth = f.readline()
HEADERS = {'Cookie':auth}

def book_info():
	req = requests.get(raw_url, headers=HEADERS).content
	soup = BeautifulSoup(req, 'html.parser')
	scripts = soup.select('script')[5].text
	book_metadata = re.findall('(?<=books:)(.*)(?=)',scripts)[0].removesuffix(',')
	book_metadata = json.loads(book_metadata)
	raw_toc = book_metadata[0]['spine']['sections']
	toc = [[1, sec['title'], int(sec['page'])] for sec in raw_toc]
	return book_metadata[0]['ws_title'], book_metadata[0]['ws_author'], book_metadata[0]['ws_isbn'], book_metadata[0]['ws_num_pages'], toc, book_metadata[0]['ws_book_id']

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f'\r[+] Downloading book... |{bar}| {percent:.2f}%', end='\r')

book_infos = book_info()
book_id = book_infos[5]

def dl():
	def get_divisions(x, n):
		result = [0]
		result.extend([x // n] * n)
		for i in range(x % n):
			result[i + 1] += 1
		return resultimport requests
from random import choice
from bs4 import BeautifulSoup
import webbrowser
import os, sys
from datetime import datetime, timedelta
from colorama import Fore

class WebRequests():
    def __init__(self, token):
        self.token = token
        self.headers: dict = {
            'Authorization': f'Bearer {self.token}',
        }

class AltadefinizioneExploit:
    def __init__(self):
        self.updated_domain = self.new_domain()
        self.session = requests.Session()
        new_user = self.register()
        self.new_token = new_user['token']
        self.new_ver_code = new_user['ver_code']
        self.new_userid = new_user['id']
        self.email = new_user['email']
        self.password = new_user['password']
        self.session.headers.update(WebRequests(self.new_token).headers)
        self.verify_email(new_user['id'], new_user['ver_code'])

    def progress_bar(self, progress, total, film_name):
        percent = 100 * (progress / float(total))
        bar = '█' * int(percent) + '-' * (100 - int(percent))
        print(f'\r[+] Downloading {film_name}... |{bar}| {percent:.2f}%', end='\r')

    def new_domain(self):
        r = requests.get('https://altadefinizione-nuovo.click/').content
        soup = BeautifulSoup(r, 'html.parser')
        domain = soup.select('h2 > a')[0].text.split('.')[-1]
        return domain

    def email_ud(self):
        email = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789%') for _ in range(10)])
        return f"{email}@{''.join([choice('abcdefghijklmnopqrstuvwxyz') for _ in range(4)])}.{''.join([choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2)])}"
    def verify_email(self, user_id, verification):
        self.session.get(f'https://altadefinizionecommunity.{self.updated_domain}/api/verify/email/{user_id}/{verification}')

    def register(self):
        rand_pass = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789%^*(-_=+)') for _ in range(10)])
        rand_email = self.email_ud()
        req = requests.post(f'https://altadefinizionecommunity.{self.updated_domain}/api/register', 
            json={"email":rand_email,"password":rand_pass,"password_confirmation":rand_pass,"fingerprint":1117459144040421,"selected_plan":1}
        ).json()
        try:
            return {
                'token': req['token'],
                'email': rand_email,
                'ver_code': req['user']['verification_code'],
                'id': req['user']['id'],
                'password': rand_pass
            }
        except Exception as e:
            print('Something went wrong. The error thrown is', e)
            print(req)

    def search_content(self, query):
        matches = []
        slugs = []
        types = []
        results = self.session.get(f'https://altadefinizionecommunity.online/api/autocomplete?search={query}').json()
        for i,r in enumerate(results['results']):
            matches.append(f"{r['text']} {Fore.CYAN}({Fore.RESET}{r['final_quality']}{Fore.CYAN}){Fore.RESET}")
            slugs.append(r['slug'])
            types.append(r['type'])
        return matches,slugs,types

    def check_media(self, url):
        r = self.session.get(f'https://altadefinizione-originale.{self.updated_domain}/api/posts/slug/{url.split("/")[-1]}').json()
        return r['post']['type']
            
    def get_serie(self, serie_url):
        serie_name = serie_url.split('?')[0].removeprefix(f'https://altadefinizionecommunity.{self.updated_domain}/p/')
        serie = self.session.get(
            f'https://altadefinizionecommunity.{self.updated_domain}/api/posts/seasons/{serie_name}',
        ).json()
        seasons = [(season['season_label'], len(season['episodes'])) for season in serie['seasons']]
        all_urls = []
        for n,season in enumerate(seasons):
            print(season[0])
            urls = []
            for episode in range(season[1]):
                print(f'    ⇢ {Fore.WHITE}Episode{Fore.RESET} {episode+1}')
                ep = []
                r = self.session.get(f'https://altadefinizionecommunity.online/api/post/urls/stream/{serie_url.split("/")[-1]}/{n}/{episode}').json()
                for stream in r['streams']:
                    ep.append(stream['url'])
                    print(f"        {Fore.WHITE}Quality{Fore.RESET}: {stream['resolution']['name']}, {stream['download_size']}")
                urls.append(ep)
            all_urls.append(urls)
        to_download = input(f'{Fore.YELLOW}●{Fore.RESET} Enter the season, episode and quality u want to download {Fore.WHITE}(format: 1-1-1){Fore.RESET}: ').split('-')
        wod = input(f'{Fore.YELLOW}●{Fore.RESET} Watch online or Download? [{Fore.GREEN}W{Fore.RESET} / {Fore.GREEN}D{Fore.RESET} / {Fore.MAGENTA}d-all{Fore.RESET} {Fore.WHITE}to download all episodes of all series{Fore.RESET}]: ').lower()
        match wod:
            case 'w':
                webbrowser.open(all_urls[int(to_download[0])-1][int(to_download[1])-1][int(to_download[2])-1])
            case 'd':
                self.download_serie([all_urls[int(to_download[0])-1][int(to_download[1])-1][int(to_download[2])-1]], token, serie_name)
            case 'd-all':
                print(f'{Fore.RED}►{Fore.RESET} Make sure you have enough disk space!')
                self.download_serie(all_urls, token, serie_name)
            case other:
                print('not a valid option')

    def download_serie(self, urls, serie_name):
        try: os.mkdir('SERIES')
        except: pass
        for n,url in enumerate(urls):
            start = time.perf_counter()
            r = self.session.ge(url, stream=True)
            total_length = int(r.headers.get('content-length'))
            file_size = 0.000001 * total_length
            dl = 0
            if total_length is None: # no content length header
              f.write(r.content)
            else:
              for chunk in r.iter_content(chunk_size = 1024*1024):
                dl += len(chunk)
                f.write(chunk)
                done = int(50 * dl / total_length)

                download_speed = round(0.000001 *(dl//(time.perf_counter() - start)), 2)
                download_time = file_size / download_speed
                current_time = time.time()
                eta = current_time + download_time
                minutes, seconds = divmod(int(eta - current_time), 60)
                hours, minutes = divmod(minutes, 60)

                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {download_speed} MB/s ETA: {round(hours,1)}:{round(minutes,1)}:{round(seconds,1)}")
                sys.stdout.flush()
        print(f'\n {serie_name} downloaded')

    def get_film(self, film_url):
        film_name = film_url.split('/')[-1]
        film = self.session.get(
            f'https://altadefinizionecommunity.{self.updated_domain}/api/post/urls/stream/{film_name}',
        ).json()

        print(f'== {Fore.GREEN}Options{Fore.RESET} ==\n')
        urls = []
        for n, stream in enumerate(film['streams']):
            urls.append(stream['url'])
            size = stream['download_size']
            res = stream['resolution']['name']
            print(f'{Fore.GREEN}[{Fore.RESET}{n+1}{Fore.GREEN}]{Fore.RESET} Quality: {res}, {size}')
        wod = input(f'\nWatch online or Download? [{Fore.GREEN}W{Fore.RESET} / {Fore.GREEN}D{Fore.RESET}]: ').lower()
        match wod:
            case 'd':
                choice = int(input(f'{Fore.YELLOW}●{Fore.RESET} Chose the resolution u want to download (enter the nuber in square brackets): '))
                self.download_film(urls[choice-1], film_name)
            case 'w':
                choice = int(input(f'{Fore.YELLOW}●{Fore.RESET} Chose the resolution you prefer to watch  (enter the nuber in square brackets): '))
                webbrowser.open(urls[choice-1], new=1, autoraise=True)

    def download_film(self, url, film_name):
        try: os.mkdir('FILMS')
        except: pass
            start = time.perf_counter()
            r = self.session.ge(url, stream=True)
            total_length = int(r.headers.get('content-length'))
            file_size = 0.000001 * total_length
            dl = 0
            if total_length is None: # no content length header
              f.write(r.content)
            else:
              for chunk in r.iter_content(chunk_size = 1024*1024):
                dl += len(chunk)
                f.write(chunk)
                done = int(50 * dl / total_length)

                download_speed = round(0.000001 *(dl//(time.perf_counter() - start)), 2)
                download_time = file_size / download_speed
                current_time = time.time()
                eta = current_time + download_time
                minutes, seconds = divmod(int(eta - current_time), 60)
                hours, minutes = divmod(minutes, 60)

                sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {download_speed} MB/s ETA: {round(hours,1)}:{round(minutes,1)}:{round(seconds,1)}")
                sys.stdout.flush()
        print(f'\n {film_name} downloaded')

    def generate_account(self):
        try: os.mkdir('ACCOUNTS')
        except: pass
        def gen():
            with open('ACCOUNTS/accounts.txt','a') as f:
                f.write(f'\n{str(datetime.now())}\n')
                f.write(f'[+] expires: {str(datetime.now() + timedelta(hours=24))}\n')
                f.write(f"[+] email: {self.email}\n")
                f.write(f"[+] password: {self.password}\n")
                f.write('='*50)
            print(f"[{Fore.GREEN}+{Fore.RESET}] {Fore.WHITE}Account generated{Fore.RESET}: {self.email} | {self.password}")
        if len(sys.argv) > 1:
             while 1: gen()
        else: gen()
        
    def download(self, url):
        if self.check_media(url) == 'movie':
            self.get_film(url)
        else:
            self.get_serie(url)


	pages_url = '{'
	if int(book_infos[3]) > 518: # 414 Request-URI Too Large
		req_nums = math.ceil(int(book_infos[3]) / 518)
		upto = get_divisions(int(book_infos[3]), req_nums)
		for i,n in enumerate(upto):
			if upto[i-1] == upto[-1]:
				start = 0
				end = n
			else:
				start = upto[i-1]
				end = int(book_infos[3]) - n + upto[i-1]
			attachment = [f'pages[]={n}&' for n in range(start, end)]
			pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{"".join(attachment)}', headers=HEADERS).text
			pages_url += pages_req
	else:
		attachment = [f'pages[]={n}&' for n in range(1, int(book_infos[3]))]
		pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{"".join(attachment)}', headers=HEADERS).text
		pages_url += pages_req

	pages_url = pages_url.replace(r'}}', ',').replace(r'{"pages":{','').removesuffix(',') + '}'
	pages_url =  json.loads(pages_url)
	doc = fitz.Document()
	progress_bar(0, book_infos[3])
	for n in range(1, int(book_infos[3])):
		try:
			page_url = pages_url[str(n)]
			page_data = requests.get(page_url, headers=HEADERS).content
			page_doc = fitz.open(stream=page_data, filetype="jpg")
			pdfbytes = page_doc.convert_to_pdf()
			doc.insert_pdf(fitz.open("pdf",pdfbytes))
		except:
			doc.new_page()
		progress_bar(n+1, book_infos[3])

	doc.set_toc(book_infos[4])
	doc.save(f'{book_infos[0]}.pdf')

print(f'''
[+] Book Found:
	- title: {book_infos[0]}
	- author: {book_infos[1]}
	- isbn: {book_infos[2]}
	- pages: {book_infos[3]}
''')
dl()
