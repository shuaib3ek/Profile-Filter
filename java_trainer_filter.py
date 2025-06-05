import streamlit as st
import pandas as pd
import io

st.title("Trainer Filter by Skill Keyword")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.success("File uploaded successfully!")

        # Show preview and column options
        st.subheader("Data Preview")
        st.dataframe(df.head())
        columns = df.columns.tolist()
        st.markdown(f"**Available columns:** {columns}")

        # User inputs skill to filter
        entered_skill = st.text_input("Enter a skill to filter trainers", "").strip().lower()

        # Search across all columns
        if st.button("Filter Trainers") and entered_skill:
            filtered_df = df[df.apply(lambda row: any(entered_skill in str(cell).lower() for cell in row), axis=1)]

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
