import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_option("deprecation.showPyplotGlobalUse", False)

import mainProgram as mp

st.markdown(
    """Welcome! This page lets you predict the like percentage of Youtube videos. Enter a video link below or
 press the checkbox to read more about the prediction."""
)

if st.checkbox("Show Prediction Info"):
    hideLink = True
    str = """Prediction is based on a subset of top-level comments from the video classified as positive, negative or
    neutral by a logistic regression classifier. The comments are fetched using the YouTube Data API. The classifier is pretrained on 3500 english Youtube-comments labeled
    positive, negative or neutral"""
    st.markdown(str)
    str = """ The prediction formula is given below: """
    st.markdown(str)
    st.latex(
        r"""
    predicted \: like \: proportion = 100 \cdot  \frac{N_{positive}+ N_{neutral}}{N_{positive}+ N_{neutral} + N_{negative}}
    """
    )
    st.markdown(""" , where """)
    st.latex("""N_{positive},\: N_{neutral} \: \& \: N_{negative}""")
    st.markdown(
        """ are the number of comments classified as positive, negative and neutral respectively. """
    )
    st.markdown(
        "[Project repo link](https://github.com/IsacLorentz/YoutubeLikePercentagePrediction)"
    )
else:

    link = st.text_input("Enter link to a Youtube video")

    if link:
        (
            foundVideoID,
            foundComments,
            videoTitle,
            channelTitle,
            predictedLikePercentage,
            actualLikePercentage,
            difference,
            mae,
            std,
            noVideos,
            noLikeInfo,
            posCloud,
            neutCloud,
            negCloud,
            barChart,
        ) = mp.program(link)

        if not foundVideoID:
            st.markdown("No Youtube Video ID was found in this link")
        elif not foundComments:
            st.markdown(
                "Comments could not be fetched for this video. Please try a different video"
            )
        else:
            str2 = (
                "Mean absolute error of "
                + str(noVideos)
                + " different videos is "
                + str(round(mae, 2))
                + " percentage points and standard deviation is "
                + str(round(std, 2))
                + " percentage points"
            )
            if noLikeInfo:
                str1 = (
                    "**predicted like percentage of this video ("
                    + videoTitle
                    + " by "
                    + channelTitle
                    + "): "
                    + str(round(predictedLikePercentage, 2))
                    + "%.**"
                )
                str3 = (
                    "This program has predicted "
                    + str(noVideos)
                    + "different videos with a mean absolute prediction error of "
                    + str(round(mae, 2))
                    + " percentage units and a standard deviation of "
                    + str(round(std, 2))
                    + " percentage points"
                )
                st.markdown(str1)
                st.markdown(str3)

            else:
                str1 = (
                    "**predicted like percentage of this video ("
                    + videoTitle
                    + " by "
                    + channelTitle
                    + "): "
                    + str(round(predictedLikePercentage, 2))
                    + "%**, actual like percentage: "
                    + str(round(actualLikePercentage, 2))
                    + "%, difference: "
                    + str(round(difference, 2))
                    + " percentage points"
                )
                st.markdown(str1)
                st.markdown(str2)

            colors = [(0.52, 0.8, 0.81), (0.22, 0.52, 0.71), (0.11, 0.18, 0.51)]
            if posCloud is not None:
                plt.imshow(posCloud)
                plt.axis("off")
                plt.title("Wordcloud of comments classified as positive")
                plt.show()
                st.pyplot()

            if neutCloud is not None:
                plt.imshow(neutCloud)
                plt.axis("off")
                plt.title("Wordcloud of comments classified as neutral")
                plt.show()
                st.pyplot()

            if negCloud is not None:
                plt.imshow(negCloud)
                plt.axis("off")
                plt.title("Wordcloud of comments classified as negative")
                plt.show()
                st.pyplot()

            fig = px.bar(
                barChart,
                x="Class",
                y="Number of comments",
                color="Number of comments",
                title="Number of comments per class",
            )
            st.write(fig)
