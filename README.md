This project is an extension of the bachelor thesis I wrote at KTH together with Gurjiwan Singh (Link: http://urn.kb.se/resolve?urn=urn:nbn:se:kth:diva-301779).

The program predicts the like percentage of any Youtube video entered by the user. Sometimes like and dislike counts are hidden on certain videos and then this program can give useful info (when comments are enabled).

Prediction is based on a subset of top-level comments from the video classified as positive, negative or neutral by a logistic regression classifier. The comments are fetched using the YouTube Data API. The classifier is pretrained on 3500 english Youtube-comments labeled positive, negative or neutral
