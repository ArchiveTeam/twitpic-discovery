'''Find valid short codes and usernames.

To use the script manually::

    python discover.py 0 1000 myfile.txt.gz


The file will contain things like:

short:abcd
user:noaheverett
tag:asdf
'''
import gzip
import re
import requests
import string
import sys
import time
import random

USER_AGENTS_LIST = ['Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0',
                    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20120101 Firefox/29.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0',
                    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36']
DEFAULT_HEADERS = {'User-Agent': random.choice(USER_AGENTS_LIST)}
ALPHABET = string.digits + string.ascii_lowercase
assert len(ALPHABET) == 10 + 26


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    output_filename = sys.argv[3]  # this should be something like myfile.txt.gz

    assert start_num <= end_num

    print('Starting', start_num, end_num)

    gzip_file = gzip.GzipFile(output_filename, 'wb')

    for shortcode in check_range(start_num, end_num):
        # Write the valid result one per line to the file
        line = '{0}\n'.format(shortcode)
        gzip_file.write(line.encode('ascii'))

    gzip_file.close()

    print('Done')


def int_to_str(num, alphabet):
    '''Convert integer to string.'''
    # http://stackoverflow.com/a/1119769/1524507
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def check_range(start_num, end_num):
    '''Check if picture exists.

    This is a generator which yields the valid shortcodes and usernames.

    Each line is like short:abcd or user:noaheverett
    '''

    for num in range(start_num, end_num + 1):
        shortcode = int_to_str(num, ALPHABET)
        url = 'http://twitpic.com/{0}'.format(shortcode)
        counter = 0

        while True:
            # Try 20 times before giving up
            if counter > 20:
                # This will stop the script with an error
                raise Exception('Giving up!')

            try:
                text = fetch(url)
            except FetchError:
                # The server may be overloaded so wait a bit
                print('Sleeping... If you see this')
                time.sleep(10)
            else:
                if text:
                    yield 'short:{0}'.format(shortcode)

                    username = extract_handle(text)

                    if username:
                        yield 'user:{0}'.format(username)

                    for tag in extract_tags(text):
                        yield 'tag:{0}'.format(tag)

                break  # stop the while loop

            counter += 1


def fetch(url):
    '''Fetch the URL and check if it returns OK.

    Returns True, returns the response text. Otherwise, returns None
    '''
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    # response doesn't have a reason attribute all the time??
    print('Got', response.status_code, getattr(response, 'reason'))

    if response.status_code == 200:
        # The item exists
        if not response.text:
            # If HTML is empty maybe server broke
            raise FetchError()

        return response.text
    elif response.status_code == 404:
        # Does not exist
        return
    else:
        # Problem
        raise FetchError()


def extract_handle(text):
    '''Return the Twitter handle from the text.'''
    # Search for something like
    # <meta name="twitter:creator" value="@noaheverett" />
    match = re.search(r'"twitter:creator"\s+value="@([a-zA-Z0-9_-]+)"', text)

    if match:
        return match.group(1)


def extract_tags(text):
    '''Return a list of tags from the text.'''
    # Search for <a href="/tag/asdf">
    return re.findall(r'"/tag/([^"]+)"', text)

if __name__ == '__main__':
    main()
