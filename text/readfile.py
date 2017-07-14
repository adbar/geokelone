import re


# load all tokens
def readplain(filename):
    with open(filename, 'r', encoding='utf-8') as inputfh:
        # splitted = inputfh.read().replace('\n', ' ').split()
        text = inputfh.read().replace('\n', ' ')
        # very basic tokenizer
        splitted = re.split(r'([^\w-]+)', text, flags=re.UNICODE) # [ .,;:]
        # build frequency dict
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
        return splitted

def readtok(filename):
    with open(filename, 'r', encoding='utf-8') as inputfh:
        i = 0
        splitted = list()
        for line in inputfh:
            i += 1
            if i % 10000000 == 0:
                print (i)
            # consider dates
            if args.dates is True:
                columns = re.split('\t', line)
                if columns[0] not in datestok:
                    datestok[columns[0]] = set()
                datestok[columns[0]].add(columns[1])
            # take only first columns
            if re.search('\t', line):
                token = re.split('\t', line)[0]
            else:
                token = line.strip()
            splitted.append(token)
        # build frequency dict
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
        return splitted


# numtokens = len(tokens)
# print ('types:', numtokens)
# print ('tokens:', len(splitted))
