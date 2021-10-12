import pickle

from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
## %matplotlib inline
from textblob import TextBlob
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import csv
import json
import random
import glob
import numpy
from scipy import stats

def classifyComments(comments, modelFile):
    loadedModel = pickle.load(open(modelFile, 'rb'))

    vectorizer = CountVectorizer(
        analyzer='word',
        lowercase=False,
    )

    vectorizedComments = vectorizer.transform(comments)
    predictions = loadedModel.predict(vectorizedComments)

    positiveCount, negativeCount, neutralCount = 0, 0, 0

    for prediction in predictions:
        if predictions[prediction] == '4':
            positiveCount += 1
        if predictions[prediction] == '2':
            neutralCount += 1
        if predictions[prediction] == '0':
            negativeCount += 1

    predictedLikePercentage = 100 * (positiveCount + neutralCount) / (positiveCount + neutralCount + negativeCount)

    return predictedLikePercentage

