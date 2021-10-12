import pickle

import pandas as pd

videoIDs = set()

pickle.dump(videoIDs, open("videoIDs.pickle", "wb"))


likePercentageDifferences = pd.DataFrame(
    dtype=float, columns=["likePercentageDifferences", "likePercentageAbsDifferences"]
)
likePercentageDifferences.to_pickle("likePercentageDifferences.pickle")
