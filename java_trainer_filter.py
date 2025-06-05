import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import base64
from io import StringIO

load_dotenv()

st.title("Trainer Bulk Email Sender (.env Only + Attachment Support)")

# Load credentials from .env only (no sidebar)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
sender_email = os.getenv("SENDER_EMAIL")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    st.session_state["full_df"] = df
    st.success("File uploaded successfully!")
    st.dataframe(df.head())

# Skill input
skill = st.text_input("Enter skill keyword (searches 'Core Areas' & 'Key Skills')", value=st.session_state.get("last_skill", "")).strip().lower()

if st.button("Filter Trainers"):
    if "full_df" in st.session_state:
        df = st.session_state["full_df"]
        filtered_df = df[
            df.apply(
                lambda row: (
                    skill in str(row.get("Core Areas", "")).lower() or
                    skill in str(row.get("Key Skills", "")).lower()
                ), axis=1
            )
        ].copy()
        st.session_state["filtered_df"] = filtered_df
        st.session_state["last_skill"] = skill

# Show filtered trainers
filtered_df = st.session_state.get("filtered_df", pd.DataFrame())
if not filtered_df.empty:
    st.success(f"Filtered {len(filtered_df)} trainer(s)")
    st.dataframe(filtered_df)

    st.markdown("### Compose Bulk Email")
    subject = st.text_input("Email Subject", key="email_subject")
    body = st.text_area("Email Body", height=200, key="email_body")

    # ✅ Attachment uploader with preview and validation
    attachment_file = st.file_uploader("Optional Attachment", type=None)
    valid_attachment = True

    if attachment_file:
        ext = attachment_file.name.split(".")[-1].lower()
        st.markdown(f"**Attached:** `{attachment_file.name}` ({attachment_file.size} bytes)")
        if ext in ["txt", "csv"]:
            preview = StringIO(attachment_file.getvalue().decode("utf-8"))
            st.code(preview.read())
        elif ext in ["xlsx"]:
            preview_df = pd.read_excel(attachment_file, engine="openpyxl")
            st.dataframe(preview_df.head())
        elif ext in ["pdf", "docx"]:
            st.info("📄 File ready to attach (preview not supported).")
        else:
            st.warning("⚠️ Unsupported file type. Only txt, csv, xlsx, pdf, docx allowed.")
            valid_attachment = False

    def get_token(client_id, client_secret, tenant_id):
        url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default"
        }
        r = requests.post(url, data=data)
        return r.json()

    def send_email(token, sender, recipient, subject, body, attachment=None):
        url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
        email_msg = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": recipient}}],
                "attachments": []
            }
        }

        if attachment:
            ext = attachment.name.split(".")[-1].lower()
            if ext not in ["txt", "csv", "xlsx", "pdf", "docx"]:
                return {"error": "Unsupported file type."}

            file_content = attachment.read()
            b64_content = base64.b64encode(file_content).decode('utf-8')
            email_msg["message"]["attachments"].append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": attachment.name,
                "contentBytes": b64_content
            })

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        return requests.post(url, headers=headers, json=email_msg)

    if client_id and client_secret and tenant_id and sender_email and subject and body:
        if st.button("Send Email to All Trainers") and valid_attachment:
            auth_response = get_token(client_id, client_secret, tenant_id)
            token = auth_response.get("access_token", "")
            if not token:
                st.error("Failed to get access token.")
                st.code(auth_response, language="json")
            else:
                success_count = 0
                for _, row in filtered_df.iterrows():
                    email = str(row.get("Email", "")).strip()
                    if email:
                        response = send_email(token, sender_email, email, subject, body, attachment_file)
                        if isinstance(response, dict) and "error" in response:
                            st.warning(f"{email}: {response['error']}")
                        elif response.status_code == 202:
                            success_count += 1
                            st.success(f"✅ Sent to {email}")
                        else:
                            st.error(f"❌ Failed to {email} ({response.status_code})")
                            st.code(response.text)
                st.info(f"✅ Emails sent: {success_count}/{len(filtered_df)}")
    else:
        st.warning("Please make sure all environment values and email fields are filled.")