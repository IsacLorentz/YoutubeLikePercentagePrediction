import json
import pickle
import re

import googleapiclient.discovery
import numpy
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

import extractComments as ec


def program(link):
    def extractVideoID(link):
        regexString = "(https?:\/\/)?(www\.)?((youtube\.(com))\/watch\?v=([-\w]+)|youtu\.be\/([-\w]+))"
        try:
            matches = list(re.findall(regexString, link)[0])
            matches = [elem for elem in matches if elem]
            videoID = matches[-1]
            if len(videoID) == 11:
                return videoID, False
            else:
                return None, True
        except:
            return None, True

    def classifyComments(comments, modelFile, vectorizerFile):

        loadedModel = pickle.load(open(modelFile, "rb"))
        loadedVectorizer = pickle.load(open(vectorizerFile, "rb"))

        predictions = loadedModel.predict(loadedVectorizer.transform(comments))

        positiveCount, negativeCount, neutralCount = 0, 0, 0
        positiveComments, neutralComments, negativeComments = [], [], []

        for i in range(0, len(predictions)):
            if predictions[i] == 4:
                positiveCount += 1
                positiveComments.append(comments[i])
            if predictions[i] == 2:
                neutralCount += 1
                neutralComments.append(comments[i])
            if predictions[i] == 0:
                negativeCount += 1
                negativeComments.append(comments[i])

        predictedLikePercentage = float(
            100
            * (positiveCount + neutralCount)
            / (positiveCount + neutralCount + negativeCount)
        )

        return (
            predictedLikePercentage,
            positiveComments,
            neutralComments,
            negativeComments,
            positiveCount,
            negativeCount,
            neutralCount,
        )

    def get_video_comments(service, video_id):
        request = service.commentThreads().list(
            videoId=video_id, part="id,snippet,replies", maxResults=100
        )
        comments = []

        while request:
            response = request.execute()

            for comment in response["items"]:
                reply_count = comment["snippet"]["totalReplyCount"]
                replies = comment.get("replies")
                if replies is not None and reply_count != len(replies["comments"]):
                    replies["comments"] = get_comment_replies(service, comment["id"])

                # 'comment' is a 'CommentThreads Resource' that has it's
                # 'replies.comments' an array of 'Comments Resource'

                # Do fill in the 'comments' data structure
                # to be provided by this function:
                comment = re.sub("\n", "", comment)
                comment = re.sub("\\s\\s+", "", comment)
                comments.append(comment)
                with open("output.txt", "a") as outputFile:
                    outputFile.write(comment + "\n")

            request = service.commentThreads().list_next(request, response)

        return comments

    def get_comment_replies(service, comment_id):
        request = service.comments().list(
            parentId=comment_id, part="id,snippet", maxResults=100
        )
        replies = []

        while request:
            response = request.execute()
            replies.extend(response["items"])
            request = service.comments().list_next(request, response)

        return replies

    def getTfidWordCloudDataframe():
        corpus = [commentsStr, posCommentsStr, neutCommentsStr, negCommentsStr]
        TfidVec = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 1), max_df=0.6, min_df=0.01
        )
        X = TfidVec.fit_transform(corpus)
        feature_names = TfidVec.get_feature_names()
        dense = X.todense()
        denselist = dense.tolist()
        wordcloudData = pd.DataFrame(denselist, columns=feature_names)
        wordcloudData = wordcloudData.transpose()
        wordcloudData.columns = [
            "totalComments",
            "posComments",
            "neutComments",
            "negComments",
        ]

        return wordcloudData

    def getWordClouds(df):

        try:
            wordcloudPos = WordCloud(
                background_color="white", width=3000, height=2000, max_words=500
            ).generate_from_frequencies(df["posComments"])
        except:
            wordcloudPos = None
        try:
            wordcloudNeut = WordCloud(
                background_color="white", width=3000, height=2000, max_words=500
            ).generate_from_frequencies(df["neutComments"])
        except:
            wordcloudNeut = None
        try:
            wordcloudNeg = WordCloud(
                background_color="white", width=3000, height=2000, max_words=500
            ).generate_from_frequencies(df["negComments"])
        except:
            wordcloudNeg = None
        return wordcloudPos, wordcloudNeut, wordcloudNeg

    videoID, fail = extractVideoID(link)
    if fail:
        return (
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    noLikeInfo = False

    with open("constants.json") as json_file:
        constants = json.load(json_file)
        constants['OAuthFile'] = st.secrets["api_key"] # replace with your API key
        ## append key

    with open("authorization/apiKey.json") as json_file:
        keys = json.load(json_file)

    total_comments = []

    # Accessing YouTube API with credentials

    youtube = googleapiclient.discovery.build(
        constants["ApiServiceName"],
        constants["ApiVersion"],
        developerKey=keys["APIKey"],
    )

    comments, commentListWithDate = ec.commentExtract(
        videoID, youtube, constants["CommentCount"]
    )
    total_comments.extend(comments)
    if not total_comments:

        return (
            True,
            False,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    likes, dislikes = ec.getLikesAndDislikes(youtube, videoID)
    if dislikes is None:
        if likes is None:
            noLikeInfo = True
        else:
            onlyLikes = True

    videoTitle, channelTitle = ec.getVideoAndChannelTitle(youtube, videoID)

    (
        result,
        positiveComments,
        neutralComments,
        negativeComments,
        positiveCount,
        negativeCount,
        neutralCount,
    ) = classifyComments(total_comments, "logRegClassifier.model", "vectorizer.pickle")

    commentsStr = str(comments)
    posCommentsStr = str(positiveComments)
    neutCommentsStr = str(neutralComments)
    negCommentsStr = str(negativeComments)

    tfidWordCloudDataframe = getTfidWordCloudDataframe()

    wordcloudPos, wordcloudNeut, wordcloudNeg = getWordClouds(tfidWordCloudDataframe)

    barChartVals = [positiveCount, negativeCount, neutralCount]
    labels = ["Positive", "Negative", "Neutral"]
    barChartValues = pd.DataFrame({"Number of comments": barChartVals, "Class": labels})

    loadedVideoIDs = pickle.load(open("videoIDs.pickle", "rb"))

    loadedLikePercentageDifferences = pd.read_pickle("likePercentageDifferences.pickle")

    if not noLikeInfo:
        actual = 100 * (likes / (likes + dislikes))
        difference = abs(result - actual)

        if videoID not in loadedVideoIDs:
            loadedVideoIDs.add(videoID)
            pickle.dump(loadedVideoIDs, open("videoIDs.pickle", "wb"))

            diff = result - actual
            absDiff = abs(diff)
            df2 = pd.DataFrame([diff, absDiff],)
            loadedLikePercentageDifferences = loadedLikePercentageDifferences.append(
                df2, ignore_index=True
            )
            loadedLikePercentageDifferences.to_pickle(
                "likePercentageDifferences.pickle"
            )

            mae = loadedLikePercentageDifferences[
                "likePercentageAbsDifferences"
            ].sum() / len(loadedLikePercentageDifferences)

            return (
                True,
                True,
                videoTitle,
                channelTitle,
                result,
                actual,
                difference,
                mae,
                numpy.std(
                    loadedLikePercentageDifferences["likePercentageAbsDifferences"],
                    ddof=1,
                ),
                len(loadedVideoIDs),
                noLikeInfo,
                wordcloudPos,
                wordcloudNeut,
                wordcloudNeg,
                barChartValues,
            )

        else:
            mae = loadedLikePercentageDifferences[
                "likePercentageAbsDifferences"
            ].sum() / len(loadedLikePercentageDifferences)
            print("mae: ", mae)
            print(
                "likeperabs: ",
                loadedLikePercentageDifferences["likePercentageDifferences"].sum(),
                type(
                    loadedLikePercentageDifferences[
                        "likePercentageAbsDifferences"
                    ].sum()
                ),
            )
            print("len: ", len(loadedLikePercentageDifferences))
            return (
                True,
                True,
                videoTitle,
                channelTitle,
                result,
                actual,
                difference,
                mae,
                numpy.std(
                    loadedLikePercentageDifferences["likePercentageDifferences"], ddof=1
                ),
                len(loadedVideoIDs),
                noLikeInfo,
                wordcloudPos,
                wordcloudNeut,
                wordcloudNeg,
                barChartValues,
            )

    else:
        mae = loadedLikePercentageDifferences[
            "likePercentageAbsDifferences"
        ].sum() / len(loadedLikePercentageDifferences)
        return (
            True,
            True,
            videoTitle,
            channelTitle,
            result,
            None,
            None,
            mae,
            numpy.std(
                loadedLikePercentageDifferences["likePercentageDifferences"], ddof=1
            ),
            len(loadedVideoIDs),
            noLikeInfo,
            wordcloudPos,
            wordcloudNeut,
            wordcloudNeg,
            barChartValues,
        )
