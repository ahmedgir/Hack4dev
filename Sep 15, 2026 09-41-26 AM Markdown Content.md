You: 

there is an event called hack4dev that i'm willing to participate in i wnt u to help me prepare for it "i;ve 1 day to prepare" but first i want to make sure that ur familiar with the hte event

ChatGPT: 

Yes — I found the event you mean, and I’m familiar enough with it now to help you prepare specifically for it rather than treating it like a generic coding hackathon.

You’re referring to **Hack4Dev Data Science Hackathon 2026 – Iraq**, connected to the international Hack4Dev initiative. The Iraq edition is being organized through the **Iraqi Space Exploration Alliance / Iraqi Astronomical Union**, under the supervision of the **International Astronomical Union (IAU)**, with local partners. It combines **data science, programming, astronomy/space-related data, machine learning, teamwork, and problem-solving**. [![](https://www.google.com/s2/favicons?domain=https://www.linkedin.com&sz=128)LinkedIn+1](https://www.linkedin.com/company/iraqi-space-exploration-alliance?utm_source=chatgpt.com)

For the current participant round, the published information says teams are **2–4 people**, participation is **in person in Baghdad at Al-Bayan University**, and participants work together on data-driven challenges. [![](https://www.google.com/s2/favicons?domain=https://www.linkedin.com&sz=128)LinkedIn+1](https://www.linkedin.com/company/iraqi-space-exploration-alliance?utm_source=chatgpt.com)

More importantly, I checked the actual Hack4Dev materials. Hack4Dev is primarily a **data-science skills hackathon**, not a normal “build a website/app in 24 hours” hackathon. Their preparation materials emphasize things like **Python, working with datasets, exploratory data analysis, visualization, and introductory machine learning**. Their official guidance specifically points participants toward Python and basic ML preparation. [![](https://www.google.com/s2/favicons?domain=https://hack4dev.org&sz=128)hack4dev.org](https://hack4dev.org/wp-content/uploads/2023/04/Hackathon-Guidelines-2.pdf?utm_source=chatgpt.com)

So with **only one day to prepare**, I would *not* try to teach you all of data science. We should optimize specifically for what will help you during Hack4Dev:

1.  **Python essentials for data science** — NumPy/Pandas, reading datasets, filtering, grouping, missing values.
    
2.  **Exploratory Data Analysis** — understanding an unfamiliar dataset quickly.
    
3.  **Visualization** — Matplotlib and interpreting graphs.
    
4.  **Basic ML** — train/test split, regression/classification, simple models, evaluation metrics.
    
5.  **Jupyter Notebook workflow** — especially important because Hack4Dev's environment uses JupyterLab. [![](https://www.google.com/s2/favicons?domain=https://github.com&sz=128)GitHub](https://github.com/Hack4Dev/Hackathon-intro?utm_source=chatgpt.com)
    
6.  **How to attack a hackathon challenge** — problem → data → hypothesis → analysis/model → insight → presentation.
    
7.  **How your team should divide roles** so you don't all spend the event writing the same code.
    
8.  **Final presentation strategy**, because a technically good solution can still lose if you cannot explain the insight clearly.
    

And there is one major advantage: **you do not need to become an ML expert tomorrow**. Hack4Dev itself describes participants as people with an interest in data science/AI/ML and basic programming experience; Python is advantageous, and the emphasis is also on learning and teamwork. [![](https://www.google.com/s2/favicons?domain=https://za.linkedin.com&sz=128)LinkedIn](https://za.linkedin.com/company/hack4dev?utm_source=chatgpt.com)

So yes: **we can prepare for the real Hack4Dev rather than guessing.**

If your event is the Baghdad Hack4Dev at **Al-Bayan University**, send me anything they gave you — challenge description, email, PDF, participant guide, datasets, WhatsApp announcement, preparation material, even screenshots. Then I can turn your **one day into a very aggressive Hack4Dev crash-prep session**, including practice challenges very close to what you'll actually face.

You: 

Hack4Dev\_Exoplanet\_Data\_Challenge\_Challenge\_Brief\_AR.pdf

PDF

I got the hachathon plan check it out for me so i can send u the challange data

ChatGPT: 

I checked the Hack4Dev challenge brief. I now understand the exact competition format, and this changes the preparation strategy. This is **not a normal app-building hackathon**; it is a **data science + scientific analysis challenge around exoplanet data**.

Hack4Dev\_Exoplanet\_Data\_Challen…

Here is the important breakdown before you send the dataset:

## 1\. The mission

You receive a package containing approximately **1,633 data records/items** related to exoplanets and astronomical observations. The goal is not to find one "correct answer"; your team must choose **one of six challenges** and produce a solution that is:

-   measurable
    
-   explainable
    
-   testable
    
-   scientifically defensible
    

The organizers explicitly say a simple, correct, explainable solution is stronger than a complex solution nobody can defend.

Hack4Dev\_Exoplanet\_Data\_Challen…

---

# The 6 possible challenges

## A — Transit Hunter ⭐ (searching for possible planets)

Goal:  
Find possible exoplanet transit signals inside light curves.

You would:

-   analyze brightness changes over time
    
-   detect repeated drops
    
-   distinguish real signals from noise
    

Output:

-   before/after light curves
    
-   candidate list
    
-   explanation why each signal matters and its confidence limits
    

Important:  
You **cannot claim "we discovered a planet"** only because you found a dip.

Hack4Dev\_Exoplanet\_Data\_Challen…

Difficulty: 🔴 High

---

## B — Analyst ⭐⭐⭐ (data analysis)

Goal:  
Understand the dataset and extract useful patterns.

You would:

-   clean data
    
-   find missing values/outliers
    
-   create visualizations
    
-   discover relationships
    

Output:

-   cleaned dataset
    
-   EDA analysis
    
-   charts
    
-   measurable findings
    

Difficulty: 🟢 Medium  
This is probably one of the safest options with 1 day preparation.

Hack4Dev\_Exoplanet\_Data\_Challen…

---

## C — ML Classifier

Goal:  
Build a machine learning model to classify/rank candidates.

You would:

-   select features
    
-   train model
    
-   evaluate with Precision/Recall/F1
    
-   analyze mistakes
    

Important:  
They specifically warn that Accuracy alone is misleading.

Hack4Dev\_Exoplanet\_Data\_Challen…

Difficulty: 🟡 Medium–High

---

## D — FITS Analysis

Goal:  
Work with astronomical FITS files.

You need:

-   astronomy file handling
    
-   metadata/header understanding
    
-   extracting measurements
    

Difficulty: 🔴 High unless your team already knows astronomy tools.

Hack4Dev\_Exoplanet\_Data\_Challen…

---

## E — Discovery Tool

Goal:  
Create an interactive exploration tool.

Example:  
A dashboard where scientists can:

-   filter candidates
    
-   compare planets
    
-   visualize properties
    

Could use:

-   Streamlit
    
-   Plotly
    

Difficulty: 🟡 Medium

This could score well because it combines analysis + usability.

Hack4Dev\_Exoplanet\_Data\_Challen…

---

## F — AI Challenge ⭐

Goal:  
Use AI/ML to:

-   detect important signals
    
-   rank candidates
    
-   reduce false positives
    

Important:  
Using AI alone does not give extra points. They care about measurable improvement and validation.

Hack4Dev\_Exoplanet\_Data\_Challen…

Difficulty: 🟡/🔴 Medium–High

---

# How they will judge you

The biggest scoring areas are:

| Area | Weight |
| --- | --- |
| Solution quality | 20% |
| Data cleaning | 15% |
| Validation/testing | 15% |
| Scientific interpretation | 15% |
| Innovation | 10% |
| Presentation | 10% |

So the winning strategy is **not the most complicated model**.

They want:

> "We asked this question → we processed the data this way → we tested it → this is why our result is trustworthy."
> 
> Hack4Dev\_Exoplanet\_Data\_Challen…

---

# With only 1 day preparation, my initial recommendation

Before seeing the dataset:

### Option 1 (most realistic):

**Challenge B + small ML component**

Example:

> "What characteristics differentiate confirmed exoplanet candidates from non-candidates?"

You can do:

-   cleaning
    
-   visualization
    
-   correlations
    
-   simple Random Forest model
    
-   feature importance
    

Very defendable.

---

### Option 2 (high presentation value):

**Challenge E**

Build:

> "Exoplanet Explorer Dashboard"

Using:

-   Python
    
-   Pandas
    
-   Streamlit
    
-   Plotly
    

Judges can immediately see the result.

---

### Option 3 (riskier but impressive):

**Challenge F**

AI ranking system:

> "Prioritize the most promising exoplanet candidates for further investigation."

---

Now send me the **challenge data files** they provided (CSV/FITS/JSON/etc.).  
After seeing the actual columns and structure, I will tell you:

1.  Which challenge gives you the highest chance to win.
    
2.  What exact idea to build.
    
3.  The architecture.
    
4.  The Python libraries needed.
    
5.  The 1-day execution plan.
    
6.  What to present to judges.
    

Sources