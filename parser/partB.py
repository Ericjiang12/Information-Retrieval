import sys
import TokenizeFile

'''
complexity O(n)
This is the main function for partB
it reads two files and prints the number of tokens that both files contain'''
if __name__ == "__main__":

    fileA = sys.argv[1]
    fileB = sys.argv[2]

    if fileA[-4:] != ".txt" or fileB[-4:] != ".txt":
        raise NameError("Invalid file type!")

    resultA = TokenizeFile._tokenize_file(fileA)
    resultB = TokenizeFile._tokenize_file(fileB)

    count = 0;
    if (len(resultA) > len(resultB)):
        for i in resultB:
            if resultA.has_key(i):
                count += 1
    else:
        for i in resultA:
            if resultB.has_key(i):
                count += 1

    print(count)
