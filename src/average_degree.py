#!/usr/bin/env python

def findKW(line, signal):
    if signal == 0:
        beg = line.find('"created_at":')
        end = line.find(',',beg)
#       timeStamp 'Thu Nov 05 05:05:39 +0000 2015'
        timeStamp = line[beg+len('"created_at":')+1:end-1]
        timeStamp = timeStamp.split(' ')
#         print timeStamp
        new = ""
#       change to form Feb 12 08:02:32 2015
        new = new + timeStamp[1] + " " + timeStamp[2] + " " + timeStamp[3]+ " " + timeStamp[5]
#         print new
        return new
    if signal == 1:
        beg = line.find('"hashtags":[')
        end = line.find('],', beg)
        hashtagstr = line[beg+len('"hashtags":['):end]
        return hashtagstr

# extract hashtag from string
# return a list
def findHT(hashtagstr):
    beg = 0
    tag =[]
    hashtag =[]
    while True:
        beg = hashtagstr.find('{"text":', beg)
        end = hashtagstr.find('}', beg)
        if beg==-1 or end == -1:
#             print 'beg=',beg, 'end=',end
            break;
        tag.append(hashtagstr[beg+len('{"text":'):end])
        beg = end + 1
    cnt = len(tag)
    for i in range(cnt):
        ht = tag[i].split(',')

        ht[0] = ht[0][1:len(ht[0])-1]
        hashtag.append(ht[0])
    # eliminate duplicates, sort hashtag and return
    h1 = Set(hashtag)
    hashtag = []
    for i in h1:
        hashtag.append(i)
    hashtag.sort()
    return hashtag

def extract(line):
    timeStamp = findKW(line,0)
#     print timeStamp
    hashtagstr = findKW(line,1)
    hashtag = findHT(hashtagstr)
#     print hashtag

    tup = [timeStamp,hashtag]
    return tup

from sets import Set
from datetime import datetime
import itertools

class hashtagGraph():
    def __init__(self):
        self.allTweets = {} # <timestamp: hashtag> dict
        self.nodes = {} # <'a',10> how many times 'a' appears
        self.edges = Set([])
        self.degree = 0.00
        self.maxTS = 'Jan 01 01:00:00 1000'

    def _delOld(self):
        print self.allTweets
        for TS in self.allTweets:
            t1 = datetime.strptime(self.maxTS, '%b %d %H:%M:%S %Y')
            t2 = datetime.strptime(TS, '%b %d %H:%M:%S %Y')
            diff = t1-t2
            if diff.total_seconds() > 60.00: # out of date, delete node and edge from graph
                self._delEdges([TS,self.allTweets[TS]])
        return


    def _delEdges(self, tweet):
        print '_delEdges',tweet
        if len(tweet[1]) <= 1: # 1 or 0 hashtag
            return
        else:
            for edge in itertools.combinations(tweet[1], 2):
                self.edges.remove(edge)

            for node in tweet[1]:
                self.nodes[node] = self.nodes[node]-1
                if self.nodes[node] == 0:
                    del self.nodes[node]

            for ht in tweet[1]:
                self.allTweets[tweet[0]].remove(ht)
                if len(self.allTweets[tweet[0]]) == 0:
                    del self.allTweets[tweet[0]]
            return

    def _addNew(self, tweet):
        if len(tweet[1]) <=1: # 1 or 0 hashtag
            return
        else:
            for edge in itertools.combinations(tweet[1], 2):
                self.edges.add(edge)
            for node in tweet[1]:
                if node in self.nodes.keys():
                    self.nodes[node] = self.nodes[node]+1
                else:
                    self.nodes[node] = 1
            return



    def update(self, newTweet):
        # add new tweet to self.allTweets
        if newTweet[0] not in self.allTweets.keys():
            self.allTweets[newTweet[0]]=[]
        for ht in newTweet[1]:
            self.allTweets[newTweet[0]].append(ht)
        print 'updated allTweets dict',self.allTweets[newTweet[0]]

#         self.allTweets.append(newTweet)
        # update maxTS
        newTS = newTweet[0]
        print 'update, newTS=', newTS
        t1 = datetime.strptime(self.maxTS, '%b %d %H:%M:%S %Y')
        t2 = datetime.strptime(newTS, '%b %d %H:%M:%S %Y')

        maxTS = max((t1, t2)) # update maximum timestamp
        self.maxTS = maxTS.strftime("%b %d %H:%M:%S %Y")

        # add new tweets to graph
        self._addNew(newTweet)

        if self.maxTS != t1:
            # max timestamp changes, delete out-of-date tweets
            self._delOld()



    def calcDegree(self):
        edgeCnt = len(self.edges)
        nodeCnt = len(self.nodes)
        degree = float(2*edgeCnt) / nodeCnt
        degree = '%.2f'% degree
        # return string degree with correct format
        return degree



from datetime import datetime
from pprint import pprint
import json
import os,sys

# read from ./tweet_input/tweets.txt
file_dir = os.path.dirname(os.path.realpath('average_degree.py'))
# file_dir = os.path.abspath(os.path.join(file_dir, os.pardir))
# print file_dir

# output file
# out = open(file_dir+'/tweet_output/output.txt','w')
out = open(sys.argv[2], 'w')

# with open(file_dir+'/tweet_input/tweets.txt') as twitter_file:
with open(sys.argv[1]) as twitter_file:
    graph = hashtagGraph()
    line = twitter_file.readline()
    while line:
        combinedTweet = extract(line)
        print combinedTweet

        graph.update(combinedTweet)
        degree = graph.calcDegree()

        degree = degree+'\r'
        out.write(degree)

        line = twitter_file.readline()
    twitter_file.close()
    out.close()
