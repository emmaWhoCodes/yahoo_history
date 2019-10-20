import urllib.request, urllib.parse, urllib.error
import time
from fake_headers import Headers

'''
Yahoo financial EOD data, however, still works on Yahoo financial pages.
These download links uses a "crumb" for authentication with a cookie "B".
This code is provided to obtain such matching cookie and crumb.
'''

# Build the cookie handler
cookier = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookier)
urllib.request.install_opener(opener)

# Cookie and corresponding crumb
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
		print(error)


#This function load the corresponding history/divident/split from Yahoo.
def load_yahoo_quote(ticker, begindate, enddate, header, info = 'quote'):
	get_cookie_crumb(ticker, info, header)

	# Prepare the parameters and the URL
	tb = time.mktime((int(begindate[0:4]), int(begindate[4:6]), int(begindate[6:8]), 4, 0, 0, 0, 0, 0))
	te = time.mktime((int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), 18, 0, 0, 0, 0, 0))

	param = dict()
	param['period1'] = int(tb)
	param['period2'] = int(te)
	param['interval'] = '1d'

	if info == 'quote':
		param['events'] = 'history'
	elif info == 'dividend':
		param['events'] = 'div'
	elif info == 'split':
		param['events'] = 'split'

	try:
		param['crumb'] = _crumb
		params = urllib.parse.urlencode(param)
		url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?{}'.format(ticker, params)
		req = urllib.request.Request(url, headers = header)

		# cookie automatically handled by opener
		f = urllib.request.urlopen(req)
		alines = f.read().decode('utf-8')
		print(alines)


	except Exception as error:
		print("There was a problem with trying to collect the data. Don't worry, this happens.")
		print("Try again in a few minutes, or with a different date range. ")
		print(error)
		return 0



def get_user_input():
	user_input = input().upper()
	print(f"Is '{user_input}' correct? 'n' to redo. Anything else to continue..")
	confirm_input = input()

	if confirm_input == "n":
		print('please enter your input')
		return get_user_input()
	return user_input.upper()


if __name__ == '__main__':

	print("Enter the stock ticker you want to scrape. Include any special characters. Hit enter after")
	ticker = get_user_input()

	print("Desired start date of data. It must be in YYYY/MM/DD format Hit enter after")
	start_date = get_user_input()
	start_date = start_date.replace("/", "")

	print("Desired end date of data. It must be in YYYY/MM/DD format. Hit enter after")
	end_date = get_user_input()
	end_date = end_date.replace("/", "")

	user_agent = Headers(headers=True).generate()['User-Agent']
	header = {'User-Agent': user_agent}

	load_yahoo_quote(ticker, start_date, end_date, header)
