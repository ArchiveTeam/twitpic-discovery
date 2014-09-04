'''Find valid short codes.'''
import requests
import string
import sys
import time
import gzip


DEFAULT_HEADERS = {'User-Agent': 'ArchiveTeam'}
ALPHABET = string.digits + string.ascii_lowercase
assert len(ALPHABET) == 10 + 26


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    output_filename = sys.argv[3]  # this should be something lile myfile.txt.gz

    assert start_num <= end_num

    print('Starting', start_num, end_num)

    gzip_file = gzip.GzipFile(output_filename, 'wb')

    for shortcode in check_range(start_num, end_num):
        # Write the valid shortcodes one per line to the file
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

    This is a generator which yields the valid shortcodes.
    '''

    for num in range(start_num, end_num + 1):
        shortcode = int_to_str(num, ALPHABET)
        url = 'http://twitpic.com/{0}'.format(shortcode)
        counter = 0

        while True:
            # Try 5 times before giving up
            if counter > 5:
                # This will stop the script with an error
                raise Exception('Giving up!')

            try:
                result = fetch(url)
            except FetchError:
                # The server may be overloaded so wait a bit
                time.sleep(5)
            else:
                if result:
                    yield shortcode

                break  # stop the while loop


def fetch(url):
    '''Fetch the URL and check if it returns OK.

    Returns True if OK. Otherwise, returns False
    '''
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    print('Got', response.status_code, response.reason)

    if response.status_code == 200:
        # The item exists
        return True
    elif response.status_code == 404:
        # Does not exist
        return False
    else:
        # Problem
        raise FetchError()


if __name__ == '__main__':
    main()
