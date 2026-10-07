# SuperKart sales forecasting UI (Streamlit)

import os

import pandas as pd
import requests
import streamlit as st

# Backend URL - container name on the shared Docker network by default
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860").rstrip("/")

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales revenue of a product in a store.")

single_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

# ---------------------- Online (single) prediction ----------------------
with single_tab:
    st.subheader("Product details")
    product_weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    product_sugar = st.selectbox("Product sugar content", ["Low Sugar", "Regular", "No Sugar"])
    product_area = st.number_input("Product allocated area (ratio)", min_value=0.0, max_value=1.0,
                                   value=0.027, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=1000.0, value=117.08, step=0.01)
    product_id_char = st.selectbox("Product family (ID prefix)", ["FD", "DR", "NC"],
                                   help="FD = Food, DR = Drinks, NC = Non-consumables")
    product_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"])

    st.subheader("Store details")
    store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
    store_city = st.selectbox("Store location city type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    store_type = st.selectbox("Store type",
                              ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"],
                              index=2)
    store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)

    if st.button("Predict sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": product_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age),
            "Product_Type_Category": product_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                st.success(f"Predicted sales: {response.json()['Predicted_Sales']:,.2f}")
            else:
                st.error(f"API error ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not reach the backend at {BACKEND_URL}: {exc}")

# ---------------------- Batch prediction ----------------------
with batch_tab:
    st.write("Upload a CSV with the 10 model features to forecast sales for many products at once.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.dataframe(batch_df.head())

        if st.button("Predict batch"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": ("batch.csv", batch_df.to_csv(index=False).encode("utf-8"), "text/csv")},
                    timeout=60,
                )
                if response.status_code == 200:
                    predictions = response.json()
                    batch_df["Predicted_Sales"] = [predictions[str(i)] for i in range(len(batch_df))]
                    st.success("Predictions complete.")
                    st.dataframe(batch_df)
                    st.download_button("Download predictions", batch_df.to_csv(index=False).encode("utf-8"),
                                       "superkart_predictions.csv", "text/csv")
                else:
                    st.error(f"API error ({response.status_code}): {response.text}")
            except requests.exceptions.RequestException as exc:
                st.error(f"Could not reach the backend at {BACKEND_URL}: {exc}")
