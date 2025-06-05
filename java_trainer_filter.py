import streamlit as st
import pandas as pd
import io

st.title("Trainer Filter by Skill")

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

        # Let user input skill to filter
        entered_skill = st.text_input("Enter a skill to filter trainers", "").strip().lower()

        # Apply filters
        if st.button("Filter Trainers"):
            filtered_df = df.copy()

            if entered_skill:
                filtered_df = filtered_df[
                    filtered_df.apply(
                        lambda row: (
                            entered_skill in str(row.get(core_col, '')).lower() or
                            entered_skill in str(row.get(skill_col, '')).lower()
                        ), axis=1
                    )
                ]

            st.success(f"Found {len(filtered_df)} matching trainer(s).")
            st.dataframe(filtered_df)

            # Download button
            towrite = io.BytesIO()
            filtered_df.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)

            st.download_button(
                label="Download Filtered Excel",
                data=towrite,
                file_name="Filtered_Trainers.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")