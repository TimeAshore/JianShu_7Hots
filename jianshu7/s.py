#conding=utf-8
import urllib
def cbk(a, b, c):
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    print '%.2f%%' % per
url = 'https://dv.phncdn.com/videos/201705/28/118208731/720P_1500K_118208731.mp4?ttl=1498100811&ri=3379200&rs=1712&hash=35ebf9b908a41f012fe0fe748c3d2a07'
urllib.urlretrieve(url,"test.mp4",cbk)