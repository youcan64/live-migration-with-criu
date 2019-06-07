from time import sleep
import os

def main():
    if(os.path.exists("output.txt")):
        os.remove("output.txt")
    f = open("output.txt",'w')
    for i in range(10):
        f.write("{}\n".format(i))
        # f.flush()
        sleep(1)
    f.close()

if __name__ == "__main__":
    main()