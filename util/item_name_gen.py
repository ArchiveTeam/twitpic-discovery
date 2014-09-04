'''Script to help generate item names.'''


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


def main():
    start_num = 0
    end_num = 2176782335
    pics_per_item = 1000

    counter = start_num
    while True:
        lower = counter
        upper = min(counter + pics_per_item, end_num)

        print('picture:{0}-{1}'.format(lower, upper))

        counter += 1000
        if counter > end_num:
            break


if __name__ == '__main__':
    main()
