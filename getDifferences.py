import pickle
loadedActualLikePercentages = pickle.load(open('actualLikePercentages.pickle', 'rb'))


loadedPredictedLikePercentages = pickle.load(open('predictedLikePercentages.pickle', 'rb'))

likePercentageAbsDifferences = []
likePercentageDifferences = []

for i in range(0, len(loadedActualLikePercentages)):
    #mae += abs(loadedPredictedLikePercentages[i] - loadedActualLikePercentages[i])
    likePercentageDifferences.append(loadedPredictedLikePercentages[i] - loadedActualLikePercentages[i])
    likePercentageAbsDifferences.append(abs(loadedPredictedLikePercentages[i] - loadedActualLikePercentages[i]))

pickle.dump(likePercentageDifferences, open('likePercentageDifferences.pickle', 'wb'))
pickle.dump(likePercentageAbsDifferences, open('likePercentageAbsDifferences.pickle', 'wb'))