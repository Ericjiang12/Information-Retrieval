import re

'''return: a dicitionary 
complexity O(n)
The function reads a file and tokenize the file into tokens
and genterates a dictionary that contains tokens as keys and occurence as value
raise NameError if file not open successfully
'''
def _tokenize_file(filename):
    bufsize = 50000
    result = dict()
    try:
        with open(filename) as infile:
            while True:
                lines = infile.readlines(bufsize)
                if not lines:
                    break
                for line in lines:
                    token = re.findall(r"[a-zA-Z0-9]+",line)
                    for i in token:
                        i = i.lower()
                        if (result.has_key(i)):
                            result[i] += 1
                        else:
                            result[i] = 1
        return result
    except:
        raise NameError("File not found!")
