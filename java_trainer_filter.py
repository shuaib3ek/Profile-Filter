
import streamlit as st
import pandas as pd
import io

st.title("Java Trainer Filter")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.success("File uploaded successfully!")

        # Show preview
        st.subheader("Data Preview")
        st.dataframe(df.head())

        # Check available columns
        columns = df.columns.tolist()
        skill_col = st.selectbox("Select the 'Key Skills' column", columns)
        core_col = st.selectbox("Select the 'Core Areas' column", columns)

        # Filter for 'java'
        if st.button("Filter Java Trainers"):
            filtered_df = df[
                df.apply(
                    lambda row: (
                        'java' in str(row.get(core_col, '')).lower() or
                        'java' in str(row.get(skill_col, '')).lower()
                    ), axis=1
                )
            ]
            st.success(f"Found {len(filtered_df)} Java trainers.")
            st.dataframe(filtered_df)

            # Download button
            towrite = io.BytesIO()
            filtered_df.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)

            st.download_button(
                label="Download Filtered Excel",
                data=towrite,
                file_name="Java_Trainers_Filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")
