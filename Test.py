import time
import pandas
import numpy as np
import matplotlib
from matplotlib import pyplot
import sys
import matplotlib.dates as mdates



def main():

    dt = matplotlib.dates.num2date(736278.769583)
    print(dt)
    print(mdates.DateFormatter('%Y.%m.%d %H:%M:%S').strftime(dt))

    sys.exit()


    s = []
    s += [('a','1')]
    print(s)
    s += [('b', '2')]
    print(s)
    sys.exit()

    now = int(time.time() * 1000)
    rangeInSec = 240

    metric = "timely.metrics.received"
    startTime = int(now - (rangeInSec * 1000))
    endTime = now

    # self.recordarr = np.rec.array([(1,2.,'Hello'),(2,3.,"World")], dtype=[('foo', 'i4'),('bar', 'f4'), ('baz', 'S10')])

    data = np.rec.array([("Mon", 5, "host1"), ('Tues', 4, 'host2')], dtype=[("date","S8"),("timely.metrics.received","i8"),("host","S8")])
    # data.dtype.names = ('date', 'timely.metrics.received', 'host')


    data = np.append(data, np.rec.array([("Wed", 5, "host1")], dtype=[("date","S8"),("timely.metrics.received","i8"),("host","S8")]))


    # np.append(data, np.rec.array([('Wed', 1234, "host1")]))



    df = pandas.DataFrame(data, columns=data.dtype.names[1:], index=data['date'])
    df.plot();
    pyplot.show(block=True)

if __name__ == '__main__':
    main()