from pyparsing import Word, WordStart, alphas, Suppress, Combine, nums, string, Optional, Regex, printables, empty
from time import strftime

class Parser(object):
    def __init__(self):

        ints = Word(nums)

        #date = Combine(ints + '-' + ints + '-' + ints)
        timestamp = Word(nums + "-" + ":" + " ")
        #time = Combine(ints + ':' + ints + ':' + ints)
        #time = Word(nums + "-" + ":")
        level = Suppress("[") + Word(alphas) + Suppress("]")
        tag = Suppress("[") + Word(printables) + Suppress("]")
        dash = Suppress("-")
        log = Regex(".*")

        self.__pattern = timestamp + level + tag + dash + log

    def parse(self, line):
        parsed = self.__pattern.parseString(line)

        payload = {}
        payload["timestamp"] = parsed[0]
        payload["level"] = parsed[1]
        #payload["timestamp"] = strftime("%Y-%m-%d %H:%M:%S")
        payload["tag"] = parsed[2]
        payload["log"] = parsed[3]
        #payload["log"] = parsed[4]

        return payload


""" --------------------------------- """


def main():
    test = "2016-09-19 17:17:11 [ERROR] [.c.d.internal.ConfigDispatcher:98   ] - Cannot activate folder watcher for folder 'conf/services': conf/services"
    parser = Parser()


    fields = parser.parse(test)
    print ("parsed:", fields)


if __name__ == "__main__":
    main()