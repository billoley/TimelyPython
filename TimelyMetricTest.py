import Timely
import time
import datetime
import json
import pandas
import getopt
import sys
import matplotlib
import seaborn
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        date = int(obj.get("timestamp")/1000);
        dateStr = datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')

        # d = {'date' : date, obj.get("metric"): obj.get("value")}
        data = []
        datatype = []
        names = []

        data += [pandas.datetime.fromtimestamp(date)]
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


        self.df = pandas.DataFrame(index=pandas.DatetimeIndex(self.data['date']))
        self.df['date'] = self.data['date']
        self.df['timely.metrics.received'] = self.data['timely.metrics.received']
        self.df.index = pandas.DatetimeIndex(self.data['date'])



        self.df = self.df.resample('1h').mean()

        print("df begin --------------------")
        print(self.df)
        print("df end --------------------")

        self.df.reset_index(inplace=True)
        print(self.df)

        # build the figure
        fig, ax = plt.subplots()
        seaborn.tsplot(self.df['timely.metrics.received'], time=matplotlib.dates.date2num(self.df.index), unit=None, interpolate=True, ax=ax, scalex=False, scaley=False)
        # sns.tsplot(df, time='Date', value='Value', unit='Unit', ax=ax)

        # assign locator and formatter for the xaxis ticks.
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y.%m.%d %H:%M:%S'))

        # put the labels at 45deg since they tend to be too long
        # fig.autofmt_xdate()
        plt.show()




        # plot = seaborn.tsplot(self.df['timely.metrics.received'], time=self.df.index, unit=None, interpolate=True, scalex=False, scaley=False)
        # seaborn.axes_style(style='dark')

        # seaborn.barplot(y=self.df['timely.metrics.received'], x=self.df.index, unit=None, units=0)

        # seaborn.barplot(y='timely.metrics.received', data=self.df)
        seaborn.plt.show()

        # self.df.plot()
        # locs, labels = pyplot.xticks()
        # pyplot.setp(labels, rotation=90)
        # pyplot.show(block=True)




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