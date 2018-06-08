import sys
import TokenizeFile

'''
complexity (O(nlogn))
The main function of part A
It takes one filename as argument
and prints out all the tokens in the file and it's occurance in decending order
'''
if __name__ == "__main__":
    filename = sys.argv[1]
    if filename[-4:] != ".txt":
        raise NameError("Invalid file type!")
    result = TokenizeFile._tokenize_file(filename)
    if result:
        for k,v in sorted(result.items(),key = lambda (k,v) : (-v,k)):
            print(k + ": "+ str(v))
    else:
        print("Empty file.")
