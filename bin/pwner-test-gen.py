import sys


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        line = " ".join(map(lambda x: x.split("/")[0], line.split(" ")))
        print(line)


if __name__ == "__main__":
    main()
