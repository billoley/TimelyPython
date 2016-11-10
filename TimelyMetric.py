import Timely
import time
import datetime
import json
import pandas
import getopt
import sys
import matplotlib
import numpy as np
from matplotlib import pyplot

from tornado import ioloop


class TimelyMetric(Timely.TimelyWebSocketClient):

    client = None
    endtime = None

    def __init__(self, metric, startTime, endTime):
        Timely.TimelyWebSocketClient.__init__(self, metric, startTime, endTime)
        self.df = pandas.DataFrame()
        self.series = pandas.Series()
        self.data = None

    def _on_message(self, msg):

        global df
        global endtime

        obj = json.loads(msg)
        date = datetime.datetime.fromtimestamp(int(obj.get("timestamp")/1000)).strftime('%Y-%m-%d %H:%M:%S')

        # d = {'date' : date, obj.get("metric"): obj.get("value")}
        data = []
        datatype = []
        names = []

        data += [(date)]
        datatype += [("date", "S20")]
        names += [("date")]

        data += [(obj.get("value"))]
        datatype += [(str(obj.get("metric")), "i8")]
        names += [(str(obj.get("metric")))]

        d = {obj.get("metric"): obj.get("value")}
        tags = obj.get("tags")[0]
        for t in tags:
            data += [(tags[t])]
            datatype += [(str(t), "S50")]
            names += [(str(t))]

        currdata = np.rec.array(data, dtype=datatype)
        currdata.dtype.names = names

        if self.data is None:
            self.data = currdata
        else:
            self.data = np.append(self.data, currdata)

        print("--------------------")
        print(datatype)
        print(self.data)
        print(self.data.dtype.names)


        timestamp = int(obj.get("timestamp"));

        if (timestamp >= self.endTime or (self.endTime - timestamp) < 60000):
            print("exiting")
            self._on_connection_close()

    def _on_connection_close(self):

        global client
        print("--------------------")
        print(self.data)
        print(self.data.dtype.names)
        print(self.data.dtype.names[1:])


        self.df = pandas.DataFrame(self.data, columns=['timely.metrics.received'], index=self.data['date'])

        print(self.df)

        plt = self.df.plot();

        locs, labels = pyplot.xticks()
        pyplot.setp(labels, rotation=90)

        pyplot.tight_layout(pad=2)


        pyplot.show(block=True)

        client.close()
        exit()


def main():

    global client
    global endtime

    # try:
    #     argv = sys.argv
    #     opts, args = getopt.getopt(argv, "hm", ["metric="])
    # except getopt.GetoptError:
    #     print 'TimelyMetric.py -m <metric>'
    #     sys.exit(2)
    # for opt, arg in args:
    #     if opt == '-h':
    #         print 'TimelyMetric.py -m <metric>'
    #         sys.exit()
    #     elif opt in ("-m", "--metric"):
    #         metric = arg
    # print 'metric is "', metric
    #

    # pyplot.plot(range(10))
    # pyplot.show(block=True)
    #
    # exit()

    now = int(time.time() * 1000)
    rangeInSec = 3600

    metric = "timely.metrics.received"
    startTime = int(now - (rangeInSec * 1000))
    endTime = now

    client = TimelyMetric(metric, startTime, endTime)
    client.connect('wss://localhost:54323/websocket')


    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()