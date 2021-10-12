"""
This is the Driver Module and Entry Point
"""
import json

# Import libraries and files
import os
import re

import createTimeSeriesData as ctsd
import getVideoIds as fid
import getVideoStatistics as vs
import google_auth_oauthlib
import googleapiclient.discovery
import mapper
import pandas as p
import predictionModels as pred
import predictionTimeSeriesModels as ptsm
import sentiment_afinn as sa
import sentiment_NRC as snrc
import sentiment_vader as sv
import streamlit as st
import visualisations as vis

import extractComments as ec

with open("constants.json") as json_file:
    constants = json.load(json_file)

with open("authorization/keys.json") as json_file:
    keys = json.load(json_file)

total_comments = []
commentsWithDate = []
total_sentiment = [(0, 0, 0)]
# Accessing YouTube API with credentials

youtube = googleapiclient.discovery.build(
    constants["ApiServiceName"],
    constants["ApiVersion"],
    developerKey=st.secrets["api_key"],
)

# kanske inte behöver skriva till en fil elr
with open("comments/" + channelName + "_vidlist.json") as json_file:
    vlist = json.load(json_file)


videoIds = [x["id"]["videoId"] for x in vlist]
stats = vs.getStatistics(youtube, videoIds)


filePath = "sentimentAnalysis/" + str(channelName) + ".txt"
sentimentFile = open(filePath, "w", encoding="utf-8")
commentsInfo = []
# Loop over the videos to extract comments and perform sentiment analysis

link = "https://www.youtube.com/watch?v=NZlClr_ivb4"
videoId = re.search("(?<=youtube.com/watch\\?v=).+", link)
videoId = videoId.group(0)
vid = videoId

comments, commentListWithDate = ec.commentExtract(
    vid, youtube, constants["CommentCount"]
)
total_comments.extend(comments)


# Write Channel stats into file
fdata = json.dumps(stats)
filePtr = open("comments/" + channelName + "_stats.json", "w")
filePtr.write(fdata)
filePtr.close()

# Write Polarity Scores of Comments into file
fdata = json.dumps(commentsWithDate)
filePtr = open("comments/" + channelName + "_comment_scores.json", "w")
filePtr.write(fdata)
filePtr.close()

sentimentFile.close()
print("Total Comments Scraped " + str(len(total_comments)))

# Getting geouped data from Time Series Data file
groupedData = ctsd.getDateWiseGrouped(channelName)
ptsm.performPredictions(groupedData, channelName)
pred.performPredictions(channelName)
vis.performVisualisations(channelName)
vis.makeWordCloud(channelName, total_comments)
