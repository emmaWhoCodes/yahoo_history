import urllib.request, urllib.parse, urllib.error
import time
from Header import Header

'''
Yahoo financial EOD data, however, still works on Yahoo financial pages.
These download links uses a "crumb" for authentication with a cookie "B".
This code is provided to obtain such matching cookie and crumb.
'''

# Build the cookie handler
cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)

_cookie = None
_crumb = None

def get_cookie_crumb(ticker, info, header):

	try:
		req = urllib.request.Request(f'https://finance.yahoo.com/{info}/{ticker}', headers = header)
		f = urllib.request.urlopen(req)
		alines = f.read().decode('utf-8')

		global _crumb
		cs = alines.find('CrumbStore')
		cr = alines.find('crumb', cs + 10)
		cl = alines.find(':', cr + 5)
		q1 = alines.find('"', cl + 1)
		q2 = alines.find('"', q1 + 1)
		crumb = alines[q1 + 1:q2]
		_crumb = crumb

		global cookier, _cookie
		for c in cookier.cookiejar:
			if c.domain != '.yahoo.com':
				continue
			if c.name != 'B':
				continue
			_cookie = c.value

	except urllib.error.HTTPError as error:
		print("There was a problem with trying to collect the data. Don't worry, this happens.")
		print("Try again in a few minutes, or with a different date range. ")
		return ""


def load_yahoo_quote(ticker, begindate, enddate, header, info = 'quote'):
	get_cookie_crumb(ticker, info, header)

	# Prepare the parameters and the URL
	tb = time.mktime((int(begindate[0:4]), int(begindate[4:6]), int(begindate[6:8]), 4, 0, 0, 0, 0, 0))
	te = time.mktime((int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), 18, 0, 0, 0, 0, 0))

	param = dict()
	param['period1'] = int(tb)
	param['period2'] = int(te)
	param['interval'] = '1d'
	param['crumb'] = _crumb

	if info == 'quote':
		param['events'] = 'history'
	elif info == 'dividend':
		param['events'] = 'div'
	elif info == 'split':
		param['events'] = 'split'

	try:
		params = urllib.parse.urlencode(param)
		url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?{}'.format(ticker, params)
		req = urllib.request.Request(url, headers = header)

		f = urllib.request.urlopen(req)
		return f.read().decode('utf-8')

	except Exception as error:
		print(error)
		return ""


def confirm_input(directions):
	print(directions)
	user_input = input().upper()
	print(f"Is '{user_input}' correct? 'n' to redo. Anything else to continue..")
	confirmation = input()

	if confirmation == "n":
		return confirm_input(directions)
	return user_input.upper()


def confirm_date(directions):
	input = confirm_input(directions)
	input = input.replace("/", "")
	month = input[0:2]
	day = input[2:4]
	year = input[4:8]
	return year + month	+ day


#This just runs a daemon like process for a user until they decides to quit.
#It allows multiple queries per session.
#TODO: multiple ticker searches in the same time interval.
if __name__ == '__main__':
	h = Header()

	while True:
		ticker_directions = "Enter the stock ticker you want to scrape. Include any special characters. Hit enter after"
		ticker = confirm_input(ticker_directions)

		start_directions = "Desired start date of data. It must be in MM/DD/YYYY format Hit enter after"
		start_date = confirm_date(start_directions)

		end_directions = "Desired end date of data. It must be in MM/DD/YYYY format. Hit enter after"
		end_date = confirm_date(end_directions)


		header = h.create_header()
		response = load_yahoo_quote(ticker, start_date, end_date, header)

		#takes a few more tries
		if response == "":
			for i in range(0, 5):
				time.sleep(20)
				header = h.create_header()
				response = load_yahoo_quote(ticker, start_date, end_date, header)
				if response != "":
					break


		if response != "":
			print('Success.Provide a filename for storage. It will be saved as a csv file')
			file = input()
			f = open(file, 'w+')
			f.write("date,open,high,low,close,adj close,volume")
			f.write(response)
		else:
			print("darn, the data couldn't be retrieved. Check the dates or ticker, or try again in a bit.")

		print("Do you want to continue? y / n")
		exit = input()
		if exit.lower() == 'n':
			break
