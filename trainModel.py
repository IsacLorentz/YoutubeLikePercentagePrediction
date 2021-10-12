import csv
import glob
import json
import pickle
import random

import matplotlib.pyplot as plt
import numpy
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.collections import LineCollection
from scipy import stats
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
## %matplotlib inline
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB, ComplementNB, MultinomialNB
from sklearn.svm import LinearSVC

YT = "C:/Users/Isac/Documents/CDATE3/DA15x/Sentiment analysis/data/tesla+annan/teslaplusyt.csv"


def main():
    train(LogisticRegression(max_iter=1000), YT)


def train(model, trainingDataset):

    data = []
    data_sentiment = []

    with open(trainingDataset, encoding="utf8") as yt_f:
        trainingData = pd.read_csv(
            yt_f, delimiter=";", names=["Comment", "CommentSentiment"]
        )

        # print(trainingData)
    # print(trainingData["Comment"].tolist())

    countVect = CountVectorizer(analyzer="word", lowercase=False,)

    # print(trainingData["Comment"].tolist())

    features = countVect.fit_transform(trainingData["Comment"].tolist())

    print("features: ", features)
    print("commensentiments: ", trainingData["CommentSentiment"].tolist())

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        trainingData["CommentSentiment"].tolist(),
        train_size=0.99,
        random_state=42,
    )

    # X_train_count = countVect.fit_transform(X_train)

    fittedModel = model.fit(X=X_train, y=y_train)
    pickle.dump(countVect, open("vectorizer.pickle", "wb"))
    pickle.dump(fittedModel, open("logRegClassifier.model", "wb"))

main()

