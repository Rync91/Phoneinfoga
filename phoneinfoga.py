#!/usr/bin/env python3

__version__ = '0.9.1-dev'

def banner():
    print("""
    ___ _                       _____        __                   
   / _ \ |__   ___  _ __   ___  \_   \_ __  / _| ___   __ _  __ _ 
  / /_)/ '_ \ / _ \| '_ \ / _ \  / /\/ '_ \| |_ / _ \ / _` |/ _` |
 / ___/| | | | (_) | | | |  __/\/ /_ | | | |  _| (_) | (_| | (_| |
 \/    |_| |_|\___/|_| |_|\___\____/ |_| |_|_|  \___/ \__, |\__,_|
|___/""")
    print("Version: {}".format(__version__))
    print("Developed by: Sundowndev")
    print("\n")

print("\033[92m")
banner()

import sys
import argparse
import random

parser = argparse.ArgumentParser(description=
    "Advanced information gathering tool for phone numbers (https://github.com/sundowndev/PhoneInfoga) version {}".format(__version__),
                                 usage='%(prog)s -n <number> [options]')

parser.add_argument('-n', '--number', metavar='number', type=str,
                    help='The phone number to scan (E164 or international format)')

parser.add_argument('-i', '--input', metavar="input_file", type=argparse.FileType('r'),
                    help='Phone number list to scan (one per line)')

parser.add_argument('-o', '--output', metavar="output_file", type=argparse.FileType('w'),
                    help='Output to save scan results')

parser.add_argument('-s', '--scanner', metavar="scanner", default="all", type=str,
                    help='The scanner to use')

parser.add_argument('--osint', action='store_true',
                    help='Use OSINT reconnaissance')

parser.add_argument('-u', '--update', action='store_true',
                    help='Update the tool & databases')

args = parser.parse_args()

# If any param is passed, execute help command
if not len(sys.argv) > 1:
    parser.print_help()
    sys.exit()

if args.update:
    print('Update')
    sys.exit()

try:
    import time
    import hashlib
    import json
    import re
    import requests
    from bs4 import BeautifulSoup
    import html5lib
    import phonenumbers
    from phonenumbers import carrier
    from phonenumbers import geocoder
    from phonenumbers import timezone
except KeyboardInterrupt:
    print('\033[91m[!] Exiting.\x1B[0m')
    sys.exit()
except:
    print('\033[91m[!] Missing requirements! Try running: pip3 install -r requirements.txt\x1B[0m')
    sys.exit()

scanners = ['any', 'all', 'numverify', 'ovh']

uagent = []
uagent.append("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14")
uagent.append("Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0")
uagent.append("Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3")
uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
uagent.append("Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7")
uagent.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1")
uagent.append("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0")

number = '' # Full number format
localNumber = '' # Local number format
internationalNumber = '' # International numberformat
numberCountryCode = '' # Dial code; e.g:"+33"
numberCountry = '' # Country; e.g:France

googleAbuseToken = ''
customFormatting = ''

def search(req, stop):
    global googleAbuseToken
    global uagent

    chosenUserAgent = random.choice(uagent)

    s = requests.Session()
    headers = {
        'User-Agent': chosenUserAgent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive',
        'Cookie': 'Cookie: CGIC=Ij90ZXh0L2h0bWwsYXBwbGljYXRpb24veGh0bWwreG1sLGFwcGxpY2F0aW9uL3htbDtxPTAuOSwqLyo7cT0wLjg; CONSENT=YES+RE.fr+20150809-08-0; 1P_JAR=2018-11-28-14; NID=148=aSdSHJz71rufCokaUC93nH3H7lOb8E7BNezDWV-PyyiHTXqWK5Y5hsvj7IAzhZAK04-QNTXjYoLXVu_eiAJkiE46DlNn6JjjgCtY-7Fr0I4JaH-PZRb7WFgSTjiFqh0fw2cCWyN69DeP92dzMd572tQW2Z1gPwno3xuPrYC1T64wOud1DjZDhVAZkpk6UkBrU0PBcnLWL7YdL6IbEaCQlAI9BwaxoH_eywPVyS9V; SID=uAYeu3gT23GCz-ktdGInQuOSf-5SSzl3Plw11-CwsEYY0mqJLSiv7tFKeRpB_5iz8SH5lg.; HSID=AZmH_ctAfs0XbWOCJ; SSID=A0PcRJSylWIxJYTq_; APISID=HHB2bKfJ-2ZUL5-R/Ac0GK3qtM8EHkloNw; SAPISID=wQoxetHBpyo4pJKE/A2P6DUM9zGnStpIVt; SIDCC=ABtHo-EhFAa2AJrJIUgRGtRooWyVK0bAwiQ4UgDmKamfe88xOYBXM47FoL5oZaTxR3H-eOp7-rE; OTZ=4671861_52_52_123900_48_436380; OGPC=873035776-8:; OGP=-873035776:;'
    }

    try:
        URL = 'https://www.google.com/search?tbs=li:1&q={}&amp;gws_rd=ssl'.format(req)
        r = s.get(URL + googleAbuseToken, headers=headers)

        while r.status_code == 503:
            print(code_warning + 'You are temporary blacklisted from Google search. Complete the captcha at the following URL and copy/paste the content of GOOGLE_ABUSE_EXEMPTION cookie: {}'.format(URL))
            print('\n' + code_info + 'Need help? Read https://github.com/sundowndev/PhoneInfoga#dealing-with-google-captcha.')
            token = input('\nGOOGLE_ABUSE_EXEMPTION=')
            googleAbuseToken = '&google_abuse=' + token
            r = s.get(URL + googleAbuseToken, headers=headers)

        soup = BeautifulSoup(r.content, 'html.parser')
        results = soup.find("div", id="search").find_all("div", class_="g")

        links = []
        counter = 0

        for result in results:
            counter += 1

            if int(counter) > int(stop):
                break

            url = result.find("a").get('href')
            url = re.sub(r'(?:\/url\?q\=)', '', url)
            url = re.sub(r'(?:\/url\?url\=)', '', url)
            url = re.sub(r'(?:\&sa\=)(?:.*)', '', url)
            url = re.sub(r'(?:\&rct\=)(?:.*)', '', url)

            if re.match(r"^(/search\?q=)", url) is not None:
                url = 'https://google.com' + url

            links.append(url)

        return links
    except:
        print(code_error + 'Request failed. Please retry or open an issue on GitHub.')

def formatNumber(InputNumber):
    return re.sub("(?:\+)?(?:[^[0-9]*)", "", InputNumber)

def localScan(InputNumber):
    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global numberCountry

    print(code_info + 'Running local scan...')

    FormattedPhoneNumber = "+" + formatNumber(InputNumber)

    try:
        PhoneNumberObject = phonenumbers.parse(FormattedPhoneNumber, None)
    except:
        return False
    else:
        if not phonenumbers.is_valid_number(PhoneNumberObject):
            return False

        number = phonenumbers.format_number(PhoneNumberObject, phonenumbers.PhoneNumberFormat.E164).replace('+', '')
        numberCountryCode = phonenumbers.format_number(PhoneNumberObject, phonenumbers.PhoneNumberFormat.INTERNATIONAL).split(' ')[0]

        countryRequest = json.loads(requests.request('GET', 'https://restcountries.eu/rest/v2/callingcode/%s' % numberCountryCode.replace('+', '')).content)
        numberCountry = countryRequest[0]['alpha2Code']

        localNumber = phonenumbers.format_number(PhoneNumberObject, phonenumbers.PhoneNumberFormat.E164).replace(numberCountryCode, '')
        internationalNumber = phonenumbers.format_number(PhoneNumberObject, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        print(code_result + 'International format: %s' % internationalNumber)
        print(code_result + 'Local format: 0%s' % localNumber)
        print(code_result + 'Country code: %s' % numberCountryCode)
        print(code_result + 'Location: %s' % geocoder.description_for_number(PhoneNumberObject, "en"))
        print(code_result + 'Carrier: %s' % carrier.name_for_number(PhoneNumberObject, 'en'))
        print(code_result + 'Area: %s' % geocoder.description_for_number(PhoneNumberObject, 'en'))
        for timezoneResult in timezone.time_zones_for_number(PhoneNumberObject):
            print(code_result + 'Timezone: %s' % (timezoneResult))

        if phonenumbers.is_possible_number(PhoneNumberObject):
            print(code_info + 'The number is valid and possible.')
        else:
            print(code_warning + 'The number is valid but might not be possible.')

def numverifyScan():
    global number

    if not args.scanner == 'numverify' and not args.scanner == 'all':
        return -1

    print(code_info + 'Running Numverify.com scan...')

    requestSecret = ''
    resp = requests.get('https://numverify.com/')
    soup = BeautifulSoup(resp.text, "html5lib")
    for tag in soup.find_all("input", type="hidden"):
        if tag['name'] == "scl_request_secret":
            requestSecret = tag['value']
            break

    apiKey = hashlib.md5()
    apiKey.update(str(number + requestSecret).encode("ascii"))
    apiKey = apiKey.hexdigest()

    headers = {
        'host': "numverify.com",
        'connection': "keep-alive",
        'content-length': "49",
        'accept': "application/json",
        'origin': "https://numverify.com",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'referer': "https://numverify.com/",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.9,fr;q=0.8,la;q=0.7,es;q=0.6,zh-CN;q=0.5,zh;q=0.4",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", "https://numverify.com/php_helper_scripts/phone_api.php?secret_key={}&number={}".format(apiKey, number), data="", headers=headers)

    if response.content == "Unauthorized" or response.status_code != 200:
        print((code_error + "An error occured while calling the API (bad request or wrong api key).\x1B[0m"))
        return -1

    data = json.loads(response.content)

    if data["valid"] == False:
        print((code_error + "Error: Please specify a valid phone number. Example: +6464806649"))
        sys.exit()

    InternationalNumber = '(' + data["country_prefix"] + ')' + data["local_format"]

    print((code_result + "Number: ({}) {}").format(data["country_prefix"],data["local_format"]))
    print((code_result + "Country: {} ({})").format(data["country_name"],data["country_code"]))
    print((code_result + "Location: {}").format(data["location"]))
    print((code_result + "Carrier: {}").format(data["carrier"]))
    print((code_result + "Line type: {}").format(data["line_type"]))

    if data["line_type"] == 'landline':
        print((code_warning + "This is most likely a landline, but it can still be a fixed VoIP number.\x1B[0m"))
    elif data["line_type"] == 'mobile':
        print((code_warning + "This is most likely a mobile number, but it can still be a VoIP number.\x1B[0m"))

def ovhScan():
    global localNumber
    global numberCountry

    if not args.scanner == 'ovh' and not args.scanner == 'all':
        return -1

    print(code_info + 'Running OVH scan...')

    querystring = {"country": numberCountry.lower()}

    headers = {
        'accept': "application/json",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", "https://api.ovh.com/1.0/telephony/number/detailedZones", data="", headers=headers, params=querystring)

    data = json.loads(response.content)

    if isinstance(data, list):
        askedNumber = "0" + localNumber.replace(localNumber[-4:], 'xxxx')

        for voip_number in data:
            if voip_number['number'] == askedNumber:
                print((code_info + "1 result found in OVH database"))
                print((code_result + "Number range: {}".format(voip_number['number'])))
                print((code_result + "City: {}".format(voip_number['city'])))
                print((code_result + "Zip Code: {}".format(voip_number['zipCode'] if voip_number['zipCode'] is not None else '')))
                askForExit()

def osintIndividualScan():
    global number
    global internationalNumber
    global numberCountryCode
    global customFormatting

    dorks = json.load(open('osint/individuals.json'))

    for dork in dorks:
        if dork['dialCode'] is None or dork['dialCode'] == numberCountryCode:
            if customFormatting:
                dorkRequest = dork['request'].replace('$n', number).replace('$i', internationalNumber) + ' | intext:"%s"' % (customFormatting)
            else:
                dorkRequest = dork['request'].replace('$n', number).replace('$i', internationalNumber)

            print((code_info + "Searching for footprints on {}...\x1B[0m".format(dork['site'])))
            for result in search(dorkRequest, stop=dork['stop']):
                if result:
                    print((code_result + "URL: " + result))
        else:
            return -1

def osintReputationScan():
    global number
    global internationalNumber
    global customFormatting

    dorks = json.load(open('osint/reputation.json'))

    for dork in dorks:
        if customFormatting:
            dorkRequest = dork['request'].replace('$n', number).replace('$i', internationalNumber) + ' | intext:"{}"'.format(customFormatting)
        else:
            dorkRequest = dork['request'].replace('$n', number).replace('$i', internationalNumber)

        print((code_info + "Searching for {}...\x1B[0m".format(dork['title'])))
        for result in search(dorkRequest, stop=dork['stop']):
            if result:
                print((code_result + "URL: " + result))

def osintSocialMediaScan():
    global number
    global internationalNumber
    global customFormatting

    dorks = json.load(open('osint/social_medias.json'))

    for dork in dorks:
        if customFormatting:
            dorkRequest = dork['request'].replace('$n', number).replace('$i', internationalNumber) + ' | intext:"{}"'.format(customFormatting)
        else:
            dorkRequest = dork['request'].replace('$n', number).replace('$i', internationalNumber)

        print((code_info + "Searching for footprints on {}...\x1B[0m".format(dork['site'])))
        for result in search(dorkRequest, stop=dork['stop']):
            if result:
                print((code_result + "URL: " + result))

def osintDisposableNumScan():
    global number

    dorks = json.load(open('osint/disposable_num_providers.json'))

    for dork in dorks:
        dorkRequest = dork['request'].replace('$n', number)

        print((code_info + "Searching for footprints on {}...\x1B[0m".format(dork['site'])))
        for result in search(dorkRequest, stop=dork['stop']):
            if result:
                print((code_result + "Result found: {}".format(dork['site'])))
                print((code_result + "URL: " + result))
                askForExit()

def osintScan():
    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global numberCountry
    global customFormatting

    if not args.osint:
        return -1

    print(code_info + 'Running OSINT footprint reconnaissance...\x1B[0m')

    # Whitepages
    print((code_info + "Generating scan URL on 411.com...\x1B[0m"))
    print(code_result + "Scan URL: https://www.411.com/phone/{}\x1B[0m".format(internationalNumber.replace('+', '').replace(' ', '-')))

    askingCustomPayload = input(code_info + 'Would you like to use an additional format for this number ? (y/N) \x1B[0m')

    if askingCustomPayload == 'y' or askingCustomPayload == 'yes':
        customFormatting = input(code_info + 'Custom format: \x1B[0m')

    print((code_info + '---- Web pages footprints ----\x1B[0m'))

    print((code_info + "Searching for footprints on web pages... (limit=5)\x1B[0m"))
    if customFormatting:
        req = '{} | intext:"{}" | intext:"{}" | intext:"{}"'.format(number, number, internationalNumber, customFormatting)
    else:
        req = '{} | intext:"{}" | intext:"{}"'.format(number, number, internationalNumber)

    for result in search(req, stop=5):
        if result:
            print((code_result + "Result found: " + result + "\x1B[0m"))

    # Documents
    print((code_info + "Searching for documents... (limit=10)"))
    if customFormatting:
        req = 'intext:"{}" | intext:"{}" | intext:"{}" ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv | ext:txt'.format(number, internationalNumber, customFormatting)
    else:
        req = 'intext:"{}" | intext:"{}" ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv | ext:txt'.format(number, internationalNumber)

    for result in search('intext:"{}" | intext:"{}" ext:doc | ext:docx | ext:odt | ext:pdf | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv | ext:txt'.format(number, internationalNumber), stop=10):
        if result:
            print((code_result + "Result found: " + result))

    print((code_info + '---- Reputation footprints ----'))

    osintReputationScan()

    print((code_info + "Generating URL on scamcallfighters.com...\x1B[0m"))
    print(code_result + 'http://www.scamcallfighters.com/search-phone-{}.html\x1B[0m'.format(number))

    tmpNumAsk = input(code_info + "Would you like to search for temporary number providers footprints? (Y/n) \x1B[0m")
    if tmpNumAsk.lower() != 'n' and tmpNumAsk.lower() != 'no':
        print((code_info + '---- Temporary number providers footprints ---m\x1B[0m'))

        print((code_info + "Searching for phone number on tempophone.com..m\x1B[0m"))
        response = requests.request("GET", "https://tempophone.com/api/v1/phones")
        data = json.loads(response.content)
        for voip_number in data['objects']:
            if voip_number['phone'] == formatNumber(number):
                print((code_result + "Found a temporary number provider: tempophone.com\x1B[0m"))
                askForExit()

        osintDisposableNumScan()

    print((code_info + '---- Social media footprints ----\x1B[0m'))

    osintSocialMediaScan()

    print((code_info + '---- Phone books footprints ----\x1B[0m'))

    if numberCountryCode == '+1':
        print((code_info + "Generating URL on True People...\x1B[0m "))
        print(code_result + 'https://www.truepeoplesearch.com/results?phoneno={}\x1B[0m'.format(internationalNumber.replace(' ', '')))

    osintIndividualScan()

def askForExit():
    if not args.output:
        user_input = input(code_info + "Continue scanning ? (y/N) \x1B[0m")

        if user_input.lower() == 'y' or user_input.lower() == 'yes':
            return -1
        else:
            print(code_info + "Goodbye!\x1B[0m")
            sys.exit()

def scanNumber(InputNumber):
    print(code_title + "[!] ---- Fetching informations for {} ---- [!]\x1B[0m".format(formatNumber(InputNumber)))

    localScan(InputNumber)

    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global numberCountry

    if not number:
        print((code_error + "Error: number {} is not valid. Skipping.\x1B[0m".format(formatNumber(InputNumber))))
        sys.exit()

    numverifyScan()
    ovhScan()
    osintScan()

    print(code_info + "Scan completed.\x1B[0m")
    print('\n')

try:
    if args.output:
        code_info = '[*] '
        code_warning = '(!) '
        code_result = '[+] '
        code_error = '[!] '
        code_title = ''

        if args.osint:
            print('\033[91m[!] OSINT scanner is not available using output option (sorry).\x1B[0m')
            sys.exit()

        sys.stdout = args.output
        banner()
    else:
        code_info = '\033[97m[*] '
        code_warning = '\033[93m(!) '
        code_result = '\033[1;32m[+] '
        code_error = '\033[91m[!] '
        code_title = '\033[1m\033[93m'

    # Verify scanner option
    if not args.scanner in scanners:
        print((code_error + "Error: scanner doesn't exists.\x1B[0m"))
        sys.exit()

    if args.number:
        scanNumber(args.number)
    elif args.input:
        for line in args.input.readlines():
            scanNumber(line)

    if args.output:
        args.output.close()
except KeyboardInterrupt:
    print((code_error + "Scan interrupted. Goodbye!\x1B[0m"))
    sys.exit()