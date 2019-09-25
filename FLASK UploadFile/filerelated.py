


def processFile(filepath):
    f=open(filepath, "r")
    if f.mode == 'r':
        contents = f.readlines()
        for l in contents:
            print(l)
        f.close()
        
