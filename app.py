import pandas as pd
import numpy as np
import plotly.express as px  # For interactive plots
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------
# Streamlit App Code with Adjustments
# -----------------------------------

# Set the page configuration
st.set_page_config(page_title="Watch Data Analysis", layout="wide")

# -----------------------------------
# 1. Load the DataFrame
# -----------------------------------


@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_watch_data_with_flags.csv")
    return df


df = load_data()

# -----------------------------------
# 1a. Data Cleaning and Standardization
# -----------------------------------

# **Ensure Correct Data Types**
df["Price_TimeZ"] = pd.to_numeric(df["Price_TimeZ"], errors="coerce")
df["Price_YourData"] = pd.to_numeric(df["Price_YourData"], errors="coerce")
df["CaseDiameter_TimeZ"] = pd.to_numeric(df["CaseDiameter_TimeZ"], errors="coerce")
df["CaseDiameter_YourData"] = pd.to_numeric(
    df["CaseDiameter_YourData"], errors="coerce"
)

# **A. Standardize Case Materials**

# Create a detailed mapping dictionary for case materials
case_material_mapping = {
    # Stainless Steel
    "stainless steel": "stainless steel",
    "steel": "stainless steel",
    "ss": "stainless steel",
    "esteel": "stainless steel",
    "polished stainless steel": "stainless steel",
    "polished stainless steel & blue yas": "stainless steel",
    "microblasted steel & yellow gold": "stainless steel and yellow gold",
    "steel with pvd coating": "stainless steel with PVD coating",
    # Gold
    "gold": "gold",
    "yellow gold": "gold",
    "18k gold": "gold",
    "18k yellow gold": "gold",
    "18k": "gold",
    "18-carat white gold": "white gold",
    "18-carat pink gold": "rose gold",
    "18-carat yellow gold": "gold",
    "18-carat sand gold": "gold",
    "18k pink gold": "rose gold",
    "18-ct rose gold": "rose gold",
    "18-ct rose gold with gold bezel": "rose gold",
    "18-ct rose gold with black ceramic bezel": "rose gold",
    "18-ct yellow gold": "gold",
    "18k white gold": "white gold",
    # Rose Gold
    "rose gold": "rose gold",
    "18k rose gold": "rose gold",
    "red gold": "rose gold",
    "pink gold": "rose gold",
    "pink gold, red gold": "rose gold",
    "rose gold, pink gold": "rose gold",
    "18k pink gold": "rose gold",
    "18-carat pink gold": "rose gold",
    "rose gold with diamond-set bezel": "rose gold",
    "rose gold, diamond": "rose gold",
    "rose gold, diamond, pink sapphire": "rose gold",
    "steel, rose gold, diamond": "stainless steel and rose gold",
    "black carbon & 18-ct rose gold": "black carbon and rose gold",
    "titanium gold": "titanium and gold",
    "stainless steel & 18-carat rose gold": "stainless steel and rose gold",
    # White Gold
    "white gold": "white gold",
    "18k white gold": "white gold",
    "platinum 950": "platinum",
    "white gold, diamond": "white gold",
    "white gold, diamond, blue sapphire": "white gold",
    "white gold, sapphire": "white gold",
    "white gold, rose gold": "white gold and rose gold",
    "white gold, ceramic": "white gold and ceramic",
    "white gold, sapphire": "white gold",
    # Titanium
    "titanium": "titanium",
    "ti": "titanium",
    "titanium dlc": "titanium DLC",
    "microblasted titanium": "titanium",
    "brushed titanium": "titanium",
    "brushed titanium & chalcedony": "titanium and chalcedony",
    "titanium,carbon": "titanium and carbon",
    "titanium,ceramic": "titanium and ceramic",
    "titanium,ceramic,bronze": "titanium, ceramic, and bronze",
    "titanium,forged carbon": "titanium and forged carbon",
    "titanium gold": "titanium and gold",
    "titanium,rose gold": "titanium and rose gold",
    "titanium,diamond": "titanium and diamond",
    # Ceramic
    "ceramic": "ceramic",
    "steel - ceramic": "stainless steel and ceramic",
    "ceramic and titanium": "ceramic and titanium",
    "black ceramic": "ceramic",
    "white ceramic": "ceramic",
    "matte white ceramic": "ceramic",
    "black matte ceramic with white ceramic bezel": "ceramic",
    "blue ceramic": "ceramic",
    "brown ceramic": "ceramic",
    "ceramic,stainless steel": "ceramic and stainless steel",
    "ceramic,titanium": "ceramic and titanium",
    "ceramic,rose gold": "ceramic and rose gold",
    "ceramic,white gold": "ceramic and white gold",
    "black microblasted ceramic": "ceramic",
    "ceramic,yellow gold": "ceramic and gold",
    # Platinum
    "platinum": "platinum",
    "platinumtech": "platinum",
    "platinum 950": "platinum",
    "950 platinum": "platinum",
    # Carbon
    "carbon": "carbon",
    "carbotech": "carbon",
    "full carbon": "carbon",
    "carbon & microblasted titanium": "carbon and titanium",
    "black carbon": "carbon",
    "black carbon & 18-ct rose gold": "black carbon and rose gold",
    "titane - carbotech": "carbon",
    "brushed titanium & chalcedony": "titanium and chalcedony",
    # Additional Materials
    "bmg-tech™": "bronze",  # Mapped to 'bronze' as a possible assumption
    "sapphire": "sapphire",
    "diamond": "diamond",
    "setting,diamonds": "diamond",
    "skeleton,gold": "skeleton and gold",
    "skeleton,rose gold": "skeleton and rose gold",
    "grey,rose gold": "grey and rose gold",
    "blue,rose gold,silver": "blue, rose gold, and silver",
    "brushed titanium & falcon's eye gemstone": "titanium and gemstone",
    "gold,gradient": "gold gradient",
    "steel, rose gold, diamond": "stainless steel, rose gold, and diamond",
}


# Function to standardize case materials
def standardize_case_material(value):
    if pd.isnull(value):
        return np.nan
    value = value.strip().lower()
    return case_material_mapping.get(value, value)


# Apply to 'CaseMaterial_YourData'
df["CaseMaterial_YourData_Std"] = df["CaseMaterial_YourData"].apply(
    standardize_case_material
)

# Apply to 'CaseMaterial_TimeZ'
df["CaseMaterial_TimeZ_Std"] = df["CaseMaterial_TimeZ"].apply(standardize_case_material)

# **B. Filter Out Case Diameters Over 70**

df = df[
    ((df["CaseDiameter_TimeZ"].isna()) | (df["CaseDiameter_TimeZ"] <= 70))
    & ((df["CaseDiameter_YourData"].isna()) | (df["CaseDiameter_YourData"] <= 70))
]

# **C. Remove Materials with Less Than 5 Occurrences and Sort Descending**

# Combine materials from both datasets
materials_timez = df["CaseMaterial_TimeZ_Std"].dropna()
materials_yourdata = df["CaseMaterial_YourData_Std"].dropna()
all_materials = pd.concat([materials_timez, materials_yourdata])

# Count occurrences
material_counts = all_materials.value_counts()

# Keep materials with at least 5 occurrences
materials_filtered = (
    material_counts[material_counts >= 5].sort_values(ascending=False).index.tolist()
)

# Update the DataFrame to include only records with materials occurring at least 5 times
df = df[
    df["CaseMaterial_TimeZ_Std"].isin(materials_filtered)
    | df["CaseMaterial_YourData_Std"].isin(materials_filtered)
]

# -----------------------------------
# 1b. Categorize Prices Based on Threshold
# -----------------------------------

# Set a fixed high price threshold
high_price_threshold = 500000  # Adjust this value as needed

# Create the 'Price_TimeZ_Category' column
df["Price_TimeZ_Category"] = df["Price_TimeZ"].apply(
    lambda x: (
        "High-Priced"
        if pd.notnull(x) and x >= high_price_threshold
        else ("Regular" if pd.notnull(x) else "Unknown")
    )
)

# -----------------------------------
# 1c. Recalculate Match Flags Based on Standardized Columns
# -----------------------------------

# Recalculate 'Price_Match'
df["Price_Match"] = df["Price_YourData"] == df["Price_TimeZ"]

# Recalculate 'CaseDiameter_Match'
df["CaseDiameter_Match"] = df["CaseDiameter_YourData"] == df["CaseDiameter_TimeZ"]

# Recalculate 'CaseMaterial_Match'
df["CaseMaterial_Match"] = (
    df["CaseMaterial_YourData_Std"] == df["CaseMaterial_TimeZ_Std"]
)

# -----------------------------------
# 2. Interactive Filters
# -----------------------------------

st.sidebar.title("Filter Options")

# **Brand Selection**
brands = df["Brand"].dropna().unique()
selected_brands = st.sidebar.multiselect(
    "Select Brands",
    options=sorted(brands),
    default=sorted(brands),
    help="Select one or more brands to include in the analysis.",
)

if not selected_brands:
    st.warning("Please select at least one brand.")
    st.stop()

# **Price Range Slider for TimeZ**
price_min_timez = float(df["Price_TimeZ"].min())
price_max_timez = float(df["Price_TimeZ"].max())
selected_price_range_timez = st.sidebar.slider(
    "Select Price Range (TimeZ)",
    min_value=price_min_timez,
    max_value=min(price_max_timez, 2000000.0),  # Cap at 2,000,000.0
    value=(price_min_timez, min(price_max_timez, 2000000.0)),
    step=1000.0,
    help="Slide to select the price range for TimeZ data.",
)

# **Price Range Slider for Brand Data**
price_min_yourdata = float(df["Price_YourData"].min())
price_max_yourdata = float(df["Price_YourData"].max())
selected_price_range_yourdata = st.sidebar.slider(
    "Select Price Range (Brand Data)",
    min_value=price_min_yourdata,
    max_value=float(price_max_yourdata),
    value=(price_min_yourdata, float(price_max_yourdata)),
    step=1000.0,
    help="Slide to select the price range for Brand Data.",
)

# **Price Category Selection**
price_categories = df["Price_TimeZ_Category"].unique()
selected_price_categories = st.sidebar.multiselect(
    "Select Price Categories",
    options=sorted(price_categories),
    default=sorted(price_categories),
    help="Select one or more price categories.",
)

if not selected_price_categories:
    st.warning("Please select at least one price category.")
    st.stop()

# **Case Material Selection**

# Use the filtered and sorted materials for selection
selected_materials = st.sidebar.multiselect(
    "Select Case Materials",
    options=materials_filtered,  # Already sorted descending by count
    default=materials_filtered,
    help="Select one or more case materials to include in the analysis.",
)

if not selected_materials:
    st.warning("Please select at least one case material.")
    st.stop()

# **Case Diameter Range Slider for TimeZ**
diameter_min_timez = float(df["CaseDiameter_TimeZ"].min())
diameter_max_timez = float(df["CaseDiameter_TimeZ"].max())
selected_diameter_range_timez = st.sidebar.slider(
    "Select Case Diameter Range (TimeZ) (mm)",
    min_value=diameter_min_timez,
    max_value=diameter_max_timez,
    value=(diameter_min_timez, diameter_max_timez),
    step=0.5,
    help="Slide to select the case diameter range for TimeZ.",
)

# **Case Diameter Range Slider for Brand Data**
diameter_min_yourdata = float(df["CaseDiameter_YourData"].min())
diameter_max_yourdata = float(df["CaseDiameter_YourData"].max())
selected_diameter_range_yourdata = st.sidebar.slider(
    "Select Case Diameter Range (Brand Data) (mm)",
    min_value=diameter_min_yourdata,
    max_value=diameter_max_yourdata,
    value=(diameter_min_yourdata, diameter_max_yourdata),
    step=0.5,
    help="Slide to select the case diameter range for Brand Data.",
)

# **Missing Data Handling**
st.sidebar.subheader("Missing Data Handling")
exclude_missing = st.sidebar.checkbox(
    "Exclude records with missing price values",
    value=True,
    help="Check to exclude records with missing price values.",
)

exclude_missing_diameter = st.sidebar.checkbox(
    "Exclude records with missing case diameter values",
    value=True,
    help="Check to exclude records with missing case diameter values.",
)

exclude_missing_material = st.sidebar.checkbox(
    "Exclude records with missing case material values",
    value=True,
    help="Check to exclude records with missing case material values.",
)

# -----------------------------------
# 3. Filter the DataFrame Based on Selections
# -----------------------------------

df_filtered = df.copy()

# **Remove watches with 'Price_TimeZ' over 2,000,000**
df_filtered = df_filtered[
    (df_filtered["Price_TimeZ"] <= 2000000.0) | (df_filtered["Price_TimeZ"].isna())
]

# **Brand Filter**
df_filtered = df_filtered[df_filtered["Brand"].isin(selected_brands)]

# **Handle Missing Data**
if exclude_missing:
    df_filtered = df_filtered.dropna(subset=["Price_TimeZ", "Price_YourData"])

if exclude_missing_diameter:
    df_filtered = df_filtered.dropna(
        subset=["CaseDiameter_TimeZ", "CaseDiameter_YourData"]
    )

if exclude_missing_material:
    df_filtered = df_filtered.dropna(
        subset=["CaseMaterial_TimeZ_Std", "CaseMaterial_YourData_Std"]
    )

# **Price Range Filters**

# Filter by selected price range for TimeZ
if exclude_missing:
    # Exclude missing prices and apply range filter
    df_filtered = df_filtered[
        (df_filtered["Price_TimeZ"] >= selected_price_range_timez[0])
        & (df_filtered["Price_TimeZ"] <= selected_price_range_timez[1])
    ]
else:
    # Include missing prices
    df_filtered = df_filtered[
        (df_filtered["Price_TimeZ"].isna())
        | (
            (df_filtered["Price_TimeZ"] >= selected_price_range_timez[0])
            & (df_filtered["Price_TimeZ"] <= selected_price_range_timez[1])
        )
    ]

# Filter by selected price range for Brand Data
if exclude_missing:
    # Exclude missing prices and apply range filter
    df_filtered = df_filtered[
        (df_filtered["Price_YourData"] >= selected_price_range_yourdata[0])
        & (df_filtered["Price_YourData"] <= selected_price_range_yourdata[1])
    ]
else:
    # Include missing prices
    df_filtered = df_filtered[
        (df_filtered["Price_YourData"].isna())
        | (
            (df_filtered["Price_YourData"] >= selected_price_range_yourdata[0])
            & (df_filtered["Price_YourData"] <= selected_price_range_yourdata[1])
        )
    ]

# **Price Category Filter**
df_filtered = df_filtered[
    df_filtered["Price_TimeZ_Category"].isin(selected_price_categories)
]

# **Case Material Filter**


def material_filter(material_series, selected_materials):
    pattern = "|".join(selected_materials)
    return material_series.str.contains(pattern, case=False, na=False)


df_filtered = df_filtered[
    material_filter(df_filtered["CaseMaterial_TimeZ_Std"], selected_materials)
    | material_filter(df_filtered["CaseMaterial_YourData_Std"], selected_materials)
]

# **Case Diameter Filters**

# Filter by selected case diameter range for TimeZ
df_filtered = df_filtered[
    (df_filtered["CaseDiameter_TimeZ"].isna())
    | (
        (df_filtered["CaseDiameter_TimeZ"] >= selected_diameter_range_timez[0])
        & (df_filtered["CaseDiameter_TimeZ"] <= selected_diameter_range_timez[1])
    )
]

# Filter by selected case diameter range for Brand Data
df_filtered = df_filtered[
    (df_filtered["CaseDiameter_YourData"].isna())
    | (
        (df_filtered["CaseDiameter_YourData"] >= selected_diameter_range_yourdata[0])
        & (df_filtered["CaseDiameter_YourData"] <= selected_diameter_range_yourdata[1])
    )
]

# -----------------------------------
# 4. Data Visualization
# -----------------------------------

st.title("TimeZ QA analysis")

st.markdown(
    """
---

### **Welcome to the TimeZ QA Analysis Dashboard!**

Here's a quick overview of the features and filters available to help you navigate the analysis:

1. **Selected Brands:**
   - **5 Brands Chosen by Default:** You can modify the selection to include or remove brands as needed.

2. **Missing Data Handling:**
   - **Excluded by Default:** To ensure data accuracy, records with missing values are excluded by default.
   - **Customizable Inclusion:** If you wish to include records with missing values, simply untick the respective checkboxes in the sidebar.

3. **Price Filters:**
   - **Price Range Slider:**
     - **TimeZ Data:** Adjust the slider to filter watches based on their price in the TimeZ dataset.
     - **Brand Data:** Similarly, filter watches based on their price in the brand's dataset.
   - **Price Categories:**
     - **Regular-Priced:** Watches priced between \$0 and \$500,000.
     - **High-Priced:** Watches priced above \$500,000.
     - **Both Categories:** View watches across both regular and high-priced categories.

4. **Case Diameter Filter:**
   - **Adjustable Range:** Use the sliders to filter watches based on their case diameter (in millimeters) for both TimeZ and Brand Data.

5. **Case Material Filter:**
   - **Top Materials Displayed:** Filter watches based on their case material, ranked in descending order of occurrence within the dataset. 

---
"""
)

# **Display Filtered Data Summary**
st.header("Filtered Data Summary")
st.write(f"Number of records after filtering: {df_filtered.shape[0]}")

# **Display Filtered Data**
with st.expander("Show Filtered Data"):
    st.dataframe(df_filtered.reset_index(drop=True))

# **H. Match Percentage Visualization**
st.header("Match Percentage between Brand Data and TimeZ")

# Calculate match percentages
total_records = len(df_filtered)
price_match_count = df_filtered["Price_Match"].sum()
price_match_percentage = (
    (price_match_count / total_records) * 100 if total_records > 0 else 0
)

diameter_match_count = df_filtered["CaseDiameter_Match"].sum()
diameter_match_percentage = (
    (diameter_match_count / total_records) * 100 if total_records > 0 else 0
)

material_match_count = df_filtered["CaseMaterial_Match"].sum()
material_match_percentage = (
    (material_match_count / total_records) * 100 if total_records > 0 else 0
)

# Create a dataframe for plotting
match_percentages = pd.DataFrame(
    {
        "Attribute": ["Price", "Case Diameter", "Case Material"],
        "Match Percentage": [
            price_match_percentage,
            diameter_match_percentage,
            material_match_percentage,
        ],
    }
)

# Plot the match percentages
fig_match = px.bar(
    match_percentages,
    x="Attribute",
    y="Match Percentage",
    labels={"Match Percentage": "Percentage (%)"},
    text="Match Percentage",
    height=500,
)
fig_match.update_traces(texttemplate="%{text:.2f}%", textposition="auto")
st.plotly_chart(fig_match, use_container_width=True)

# **F. Match Flags Distribution**
st.header("Match Distribution")

col7, col8, col9 = st.columns(3)

# Map boolean values to labels
df_filtered["Price_Match_Label"] = df_filtered["Price_Match"].map(
    {True: "Match", False: "Mismatch"}
)
df_filtered["CaseDiameter_Match_Label"] = df_filtered["CaseDiameter_Match"].map(
    {True: "Match", False: "Mismatch"}
)
df_filtered["CaseMaterial_Match_Label"] = df_filtered["CaseMaterial_Match"].map(
    {True: "Match", False: "Mismatch"}
)

with col7:
    st.subheader("")
    price_match_counts = df_filtered["Price_Match_Label"].value_counts().reset_index()
    price_match_counts.columns = ["Match Status", "Count"]
    fig9 = px.bar(
        price_match_counts,
        x="Match Status",
        y="Count",
        color="Match Status",
        labels={"Match Status": "Price Match", "Count": "Count"},
        title="Price Match Distribution",
        width=350,  # Adjust width to make plot thinner
        height=400,
    )
    st.plotly_chart(fig9)

with col8:
    st.subheader("")
    diameter_match_counts = (
        df_filtered["CaseDiameter_Match_Label"].value_counts().reset_index()
    )
    diameter_match_counts.columns = ["Match Status", "Count"]
    fig10 = px.bar(
        diameter_match_counts,
        x="Match Status",
        y="Count",
        color="Match Status",
        labels={"Match Status": "Case Diameter Match", "Count": "Count"},
        title="Case Diameter Match Distribution",
        width=350,  # Adjust width to make plot thinner
        height=400,
    )
    st.plotly_chart(fig10)

with col9:
    st.subheader("")
    material_match_counts = (
        df_filtered["CaseMaterial_Match_Label"].value_counts().reset_index()
    )
    material_match_counts.columns = ["Match Status", "Count"]
    fig11 = px.bar(
        material_match_counts,
        x="Match Status",
        y="Count",
        color="Match Status",
        labels={"Match Status": "Case Material Match", "Count": "Count"},
        title="Case Material Match Distribution",
        width=350,  # Adjust width to make plot thinner
        height=400,
    )
    st.plotly_chart(fig11)

# **G. Median Price Comparison by Brand**
st.header("Median Price Comparison by Brand")

median_price = (
    df_filtered.groupby("Brand")
    .agg(
        Median_Price_YourData=("Price_YourData", "median"),
        Median_Price_TimeZ=("Price_TimeZ", "median"),
    )
    .reset_index()
)
median_price = median_price.dropna(how="all")

fig13 = go.Figure()
fig13.add_trace(
    go.Bar(
        x=median_price["Brand"],
        y=median_price["Median_Price_YourData"],
        name="Brand Data",
        text=median_price["Median_Price_YourData"],
        textposition="auto",
    )
)
fig13.add_trace(
    go.Bar(
        x=median_price["Brand"],
        y=median_price["Median_Price_TimeZ"],
        name="TimeZ",
        text=median_price["Median_Price_TimeZ"],
        textposition="auto",
    )
)
fig13.update_layout(
    barmode="group",
    xaxis_tickangle=-45,
    xaxis_title="Brand",
    yaxis_title="Median Price",
    height=600,
)
fig13.update_yaxes(tickformat="$,.0f")
st.plotly_chart(fig13, use_container_width=True)

# **A. Histograms for Price Distribution**
st.header("Price Distribution")

col1, col2 = st.columns(2)

with col1:
    st.subheader("")
    fig1 = px.histogram(
        df_filtered,
        x="Price_YourData",
        nbins=50,
        title="Price Distribution - Brand Data",
        labels={"Price_YourData": "Price"},
        height=500,
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("")
    fig2 = px.histogram(
        df_filtered,
        x="Price_TimeZ",
        nbins=50,
        title="Price Distribution - TimeZ",
        labels={"Price_TimeZ": "Price"},
        height=500,
    )
    st.plotly_chart(fig2, use_container_width=True)

# **E. Bar Chart: Case Material Distribution**
st.header("Case Material Distribution Comparison (Top 10 Materials)")

# For this plot, we will get the top 10 materials by total occurrences in both datasets

# Combine materials from both datasets in df_filtered
materials_yourdata_filtered = df_filtered["CaseMaterial_YourData_Std"].dropna()
materials_timez_filtered = df_filtered["CaseMaterial_TimeZ_Std"].dropna()
all_materials_filtered = pd.concat(
    [materials_yourdata_filtered, materials_timez_filtered]
)

# Get counts
material_counts_filtered = all_materials_filtered.value_counts()

# Get top 10 materials
top10_materials = material_counts_filtered.nlargest(10).index.tolist()

# Filter the materials_df to include only top 10 materials
materials_yourdata = (
    df_filtered["CaseMaterial_YourData_Std"].value_counts().rename("Brand Data")
)
materials_timez = df_filtered["CaseMaterial_TimeZ_Std"].value_counts().rename("TimeZ")

materials_df = pd.concat([materials_yourdata, materials_timez], axis=1).fillna(0)
materials_df = materials_df.reset_index().rename(columns={"index": "CaseMaterial"})
materials_df_top10 = materials_df[materials_df["CaseMaterial"].isin(top10_materials)]

fig8 = go.Figure()
fig8.add_trace(
    go.Bar(
        x=materials_df_top10["CaseMaterial"],
        y=materials_df_top10["Brand Data"],
        name="Brand Data",
        text=materials_df_top10["Brand Data"],
        textposition="auto",
    )
)
fig8.add_trace(
    go.Bar(
        x=materials_df_top10["CaseMaterial"],
        y=materials_df_top10["TimeZ"],
        name="TimeZ",
        text=materials_df_top10["TimeZ"],
        textposition="auto",
    )
)

fig8.update_layout(
    barmode="group",
    xaxis_tickangle=-45,
    xaxis_title="Case Material",
    yaxis_title="Count",
    height=600,
)
st.plotly_chart(fig8, use_container_width=True)
