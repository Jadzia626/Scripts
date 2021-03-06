#!/usr/bin/env python3
#
#  Pull Latest Binance Crypto Rate for a Given Pair
# ==================================================
#  Author:  Veronica Berglyd Olsen
#  Date:    04.04.2018
#  URL:     https://github.com/vkbo/Scripts
#

import json
import sys
import os
import signal
import numpy

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from time import time, sleep
from datetime import datetime

# Settings
maxHist = 5000

# Make JSON API Call
def getJSON(apiCall):
    urlReq = Request(apiCall)
    urlReq.add_header("User-Agent", "Mozilla/5.0 (compatible; Python script)")
    urlReq.add_header("Content-Type", "application/json")
    try:
        urlData = urlopen(urlReq, timeout=10)
        return json.loads(urlData.read().decode())
    except HTTPError as htpErr:
        print("HTTP Error %3d: %s" % (htpErr.code, htpErr.reason))
        if htpErr.code == 429:
            sleep(60)
        elif htpErr.code == 418:
            sleep(300)
        return {"Error": True}
    except URLError as urlErr:
        print("URL Error: %s" % urlErr.reason)
        return {"Error": True}
    except Exception:
        print("Unknown Error")
        return {"Error": True}

def signalHandler(theSignal, theFrame):
    print("\nExiting ...")
    sys.exit(0)

def stringToSeconds(timeString):
    if len(timeString) >= 2:
        if timeString[-1] == "s":
            return float(timeString[:-1])
        elif timeString[-1] == "m":
            return float(timeString[:-1])*60
        elif timeString[-1] == "h":
            return float(timeString[:-1])*3600
    print("Error: Could not parse time string '%s'" % timeString)
    print("       Format is 00s, 00m or 00h")
    sys.exit(0)
    return

def formatTime(tS):
    return f"{tS//3600:02d}:{tS%3600//60:02d}:{tS%60:02d}"

# Capture ctrl+c
signal.signal(signal.SIGINT, signalHandler)

# Linux Terminal Colours
RED       = "\033[0;31m"
GREEN     = "\033[0;32m"
YELLOW    = "\033[0;33m"
BLUE      = "\033[0;34m"
PURPLE    = "\033[0;35m"
CYAN      = "\033[0;36m"
BOLD      = "\033[0;1m"
UNDERLINE = "\033[0;4m"
END       = "\033[0;0m"

# Get initial info
okPairs = {}
apiCall = "https://api.binance.com/api/v1/exchangeInfo"
apiJSON = getJSON(apiCall)
if "Error" in apiJSON.keys():
    print("Stopping ...")
    sys.exit(1)
for exPair in apiJSON["symbols"]:
    okPairs[exPair["symbol"]] = exPair["quoteAsset"]

if len(sys.argv) < 3:
    print((
        "Error: No currency pair specified\n"
        "Usage: %s [interval]/[trend]/[trend] PAIR1 PAIR2 ...\n"
        "       %s [interval]/[trend]/[trend] pairFile.dat\n"
        "Where: [interval] is the refresh time in units of s, m or h. E.g. 10s\n"
        "       [trend]    is optionally the time to calculate hourly trends\n"
        "                  over, in units of s, m or h. Two such trend times\n"
        "                  can be calculated. It is assumed that the second\n"
        "                  one is shorter than the first. These are labelled\n"
        "                  ST and LT for Short and Long Trend.\n"
        "       PAIR1...n  are the exchange pairs. See Binance exchange for\n"
        "                  valid pairs. Alternatively, a file of pairs to\n"
        "                  monitor that will be read every cycle.\n"
    ) % (
        os.path.basename(sys.argv[0]), os.path.basename(sys.argv[0])
    ))
    sys.exit(1)

theFile  = sys.argv[2]
theCoins = sys.argv[2:]
useFile  = os.path.isfile(theFile)
inTemp   = sys.argv[1]
inSplit  = inTemp.split("/")
theWait  = stringToSeconds(inSplit[0])

xSort = {}
for n, theCoin in enumerate(theCoins):
    xSort[theCoin] = -n

if len(inSplit) > 1:
    theLTrend = stringToSeconds(inSplit[1])+0.49*theWait
else:
    theLTrend = theWait*24

if len(inSplit) > 2:
    theSTrend = stringToSeconds(inSplit[2])+0.49*theWait
else:
    theSTrend = 0.0

if theLTrend/theWait > maxHist:
    maxHist = round(theLTrend/theWait)+10

theHist = {}
theTime = {}

lSpan = 0
sSpan = 0
wLen  = 92
if theLTrend > 0.0:
    wLen += 10
if theSTrend > 0.0:
    wLen += 11

while True:

    toPrint  = "Every %.1f seconds:" % theWait
    toPrint += " "*(wLen-len(toPrint)-19)
    toPrint += datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')+"\n"
    toPrint += "\n"

    if useFile:
        theCoins = []
        with open(theFile, mode="r") as inFile:
            for inLine in inFile:
                inLine = inLine.strip()
                if len(inLine) < 5:
                    continue
                if inLine[0] == "#":
                    continue
                theCoins.append(inLine)
                if inLine not in xSort.keys():
                    xSort[inLine] = 0
        delCoin = []
        for theCoin in xSort.keys():
            if theCoin not in theCoins:
                delCoin.append(theCoin)
        for theCoin in delCoin:
            del xSort[theCoin]

    theSorted = sorted(xSort.items(), key=lambda x: x[1], reverse=True)
    xSort = {}

    for theCoin, theKey in theSorted:

        if theCoin == "":
            continue

        if theCoin not in okPairs.keys():
            toPrint += f"{BOLD}%-11s{END} " % theCoin
            toPrint += f"{RED}Invalid trading pair{END}\n"
            continue

        if theCoin not in theHist:
            theHist[theCoin] = []
            theTime[theCoin] = []

        apiCall = "http://api.binance.com/api/v1/ticker/24hr?symbol=%s" % theCoin
        apiJSON = getJSON(apiCall)

        if "Error" in apiJSON.keys():
            continue

        theSymbol = apiJSON["symbol"]
        lastPrice = float(apiJSON["lastPrice"])
        lowPrice  = float(apiJSON["lowPrice"])
        highPrice = float(apiJSON["highPrice"])
        openPrice = float(apiJSON["openPrice"])
        qVolume   = float(apiJSON["quoteVolume"])
        cVolume   = float(apiJSON["volume"])
        if lastPrice * lowPrice * highPrice * openPrice == 0.0:
            toPrint += f"{BOLD}%-11s{END} " % theSymbol
            toPrint += f"{RED}Unexpected zero values returned.{END}\n"
            continue

        change24h = 100*(lastPrice-openPrice)/openPrice
        stochOsc  = 100*(lastPrice-lowPrice)/(highPrice-lowPrice)

        timeNow   = time()
        theHist[theCoin].append(lastPrice)
        theTime[theCoin].append(timeNow)
        xSort[theCoin] = lastPrice

        nHist  = len(theHist[theCoin])
        yFit   = (0, 0)
        lTrend = 0.0
        sTrend = 0.0
        if nHist > 1:
            if theLTrend > 0.0:
                xTimes = [i for i in theTime[theCoin] if i >= timeNow-theLTrend]
                nTimes = len(xTimes)
                xData  = numpy.linspace(0, theWait*(nTimes-1), nTimes)
                yFit   = numpy.polyfit(theTime[theCoin][-nTimes:], theHist[theCoin][-nTimes:], 1)
                lSpan  = timeNow-xTimes[0]
                lTrend = 360000*yFit[0]/lastPrice
            else:
                lTrend = 0.0
            if theSTrend > 0.0:
                xTimes = [i for i in theTime[theCoin] if i >= timeNow-theSTrend]
                nTimes = len(xTimes)
                xData  = numpy.linspace(0, theWait*(nTimes-1), nTimes)
                yFit   = numpy.polyfit(theTime[theCoin][-nTimes:], theHist[theCoin][-nTimes:], 1)
                sSpan  = timeNow-xTimes[0]
                sTrend = 360000*yFit[0]/lastPrice
            else:
                sTrend = 0
        if nHist > maxHist:
            theHist[theCoin].pop(0)
            theTime[theCoin].pop(0)

        if okPairs[theCoin] == "BTC":
            fmtNum = "%10.8f"
        elif okPairs[theCoin] == "ETH":
            fmtNum = "%10.7f"
        elif okPairs[theCoin] == "BNB":
            fmtNum = "%10.6f"
        elif okPairs[theCoin] == "USDT":
            fmtNum = "%10.4f"
        else:
            fmtNum = "%10.6f"

        if okPairs[theCoin] == "BTC":
            qVolume *= 1e-3
            volSc    = "K"
        else:
            qVolume *= 1e-6
            volSc    = "M"

        toPrint += f"{BOLD}%-11s{END} " % theSymbol
        toPrint += f"{CYAN}{fmtNum}{END} " % lastPrice
        toPrint += f"{YELLOW}(L:{fmtNum} H:{fmtNum} O:{fmtNum} V:%7.2f%s){END} " % (
            lowPrice, highPrice, openPrice, qVolume, volSc
        )
        if change24h < 0:
            toPrint += f"{RED}%+7.2f%%{END}" % change24h
        else:
            toPrint += f"{GREEN}%+7.2f%%{END}" % change24h

        toPrint += "  "
        if theLTrend > 0.0:
            if lTrend < -99.99:
                toPrint += f"{RED}L:<99.99%{END}"
            elif lTrend < 0.00:
                toPrint += f"{RED}L:%+6.2f%%{END}" % lTrend
            elif lTrend < 100.00:
                toPrint += f"{GREEN}L:%+6.2f%%{END}" % lTrend
            else:
                toPrint += f"{GREEN}L:>99.99%{END}"
        if theSTrend > 0.0:
            if sTrend < -99.99:
                toPrint += f" {RED}S:<99.99%{END}"
            elif sTrend < 0.00:
                toPrint += f" {RED}S:%+6.2f%%{END}" % sTrend
            elif sTrend < 100.00:
                toPrint += f" {GREEN}S:%+6.2f%%{END}" % sTrend
            else:
                toPrint += f" {GREEN}S:>99.99%{END}"

        if stochOsc >= 99.9:
            toPrint += f"  {RED}%K:99.9{END}"
        elif stochOsc >= 90.0:
            toPrint += f"  {RED}%%K:%4.1f{END}" % stochOsc
        elif stochOsc >= 75.0:
            toPrint += f"  {YELLOW}%%K:%4.1f{END}" % stochOsc
        elif stochOsc >= 25.0:
            toPrint += f"  {GREEN}%%K:%4.1f{END}" % stochOsc
        elif stochOsc >= 10.0:
            toPrint += f"  {YELLOW}%%K:%4.1f{END}" % stochOsc
        elif stochOsc > 0.0:
            toPrint += f"  {RED}%%K:%4.1f{END}" % stochOsc
        else:
            toPrint += f"  {RED}%K: 0.0{END}"

        toPrint += "\n"

    toPrint += "\n"
    prTrend  = "Hourly Trends: "
    if lSpan > 0.0:
        prTrend += "L:" + formatTime(round(lSpan))
    if sSpan > 0.0:
        prTrend += ", S:" + formatTime(round(sSpan))
    if lSpan + sSpan == 0.0:
        prTrend += "00:00:00"
    prTrend += ". Stochastic Osc. 24h."

    # Calculate sleep time
    if nHist > 1:
        actTime  = theTime[theCoin][-1]-theTime[theCoin][0]
        wantTime = theWait*(nHist-1)
        diffTime = wantTime-actTime
        toWait   = theWait+diffTime
        if toWait < 0:
            toWait = 0.5
        prTime   = "Avg. Time: %.2f seconds" % (actTime/(nHist-1))
    else:
        prTime = ""
        toWait = theWait

    toPrint += prTrend+(" "*(wLen-len(prTrend)-len(prTime)))+prTime

    print("\033[H\033[J", end="")
    sys.stdout.flush()
    print(toPrint)
    sys.stdout.flush()
    sleep(toWait)
