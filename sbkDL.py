import requests, os, shutil
from natsort import natsorted
from PIL import Image

try: os.mkdir('pages')
except: pass

book_id = input('Enter the book url: \n').split('/')[4]
with open('cookies.txt', 'r') as f: auth = f.readline()
HEADERS = {'Cookie':auth}
npages = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/plus', headers=HEADERS).json()[-1]['page']

def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f'\r Downloading book... |{bar}| {percent:.2f}%', end='\r')

attachment = [f'pages[]={n}&' for n in range(1, int(npages)+1)]
params = ''.join(attachment)
pages_req = requests.get(f'https://webapp.scuolabook.it/books/{book_id}/pages?{params}', headers=HEADERS).json()

progress_bar(0, npages)
for n in range(1, int(npages)+1):
	page_url = pages_req['pages'][str(n)]
	page_data = requests.get(page_url, headers=HEADERS).content
	with open(f'pages/page{n}.png', 'wb') as image:
		image.write(page_data)
	progress_bar(n+1, npages)

def create_pdf():
	file_names = os.listdir('pages')
	file_names = natsorted(file_names)
	pdfimages = [Image.open(f'pages/{f}') for f in file_names]
	pdf_path = 'book' + '.pdf'
	pdfimages[0].save(pdf_path, "PDF" , resolution=100.0, save_all=True, append_images=pdfimages[1:])
	shutil.rmtree('pages')
	print('Done :)')

create_pdf()