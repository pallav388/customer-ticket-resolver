import streamlit as st
from tools.sheet_connector import (
    fetch_new_tickets,
    update_ticket,
    append_processed_ticket
)
from tools.classify_ticket import classify_ticket
from tools.generate_ticket import generate_reply
from tools.gmail_sender import send_email_smtp
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Ticket Manager", layout="centered")

st.title("📩 AI BASED CUSTOMER SUPPORTR")
st.caption("Analyze, classify, respond, and track customer support tickets - powered by AI.")

tickets = fetch_new_tickets()

if not tickets:
    st.success("✅ No new tickets to process.")
else:
    for i, ticket in enumerate(tickets):
        if ticket.get('Sentiment') and ticket.get('AutoReply'):
            continue

        ticket_name = ticket.get("Name", "Unknown")
        ticket_email = ticket.get("Email", "Unknown")
        ticket_message = ticket.get("Message", "No message provided")

        with st.expander(f"📩 Ticket #{i + 1} from {ticket_name} ({ticket_email})"):
            st.markdown("**📨 Message:**")
            st.info(ticket_message)

            if st.button(f"🔵 Analyze & Respond Ticket #{i + 1}"):
                with st.spinner("🤖 Running AI classification and reply generation..."):
                    try:
                        classification = classify_ticket(ticket_message)
                        reply = generate_reply(ticket_message)
                    except Exception as e:
                        st.error(f"❌ Error during AI processing: {str(e)}")
                        continue

                st.success("✅ AI Analysis Complete")
                st.markdown(f"**Sentiment:** {classification.get('sentiment', 'N/A')}")
                st.markdown(f"**Issue Type:** {classification.get('issue_type', 'N/A')}")
                st.markdown("**👍 Suggested Reply:**")
                st.text_area("Auto-Generated Reply", reply, height=140)

                try:
                    update_ticket(
                        row_number=ticket["__row_number__"],
                        sentiment=classification.get("sentiment", ""),
                        issue_type_label=classification.get("issue_type", ""),
                        reply=reply
                    )
                except Exception as e:
                    st.error(f"❌ Error updating the ticket: {str(e)}")
                    continue

                try:
                    append_processed_ticket(
                        ticket=ticket,
                        sentiment=classification.get("sentiment", ""),
                        issue_type_label=classification.get("issue_type", ""),
                        reply=reply
                    )
                except Exception as e:
                    st.error(f"❌ Error appending to processed tickets: {str(e)}")
                    continue

                with st.spinner("📧 Sending email reply..."):
                    try:
                        success = send_email_smtp(
                            to=ticket_email,
                            subject="Regarding Your Support Ticket",
                            body=reply
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {str(e)}")
                        continue

                if success["status"] == "success":
                    st.success("📬 Email sent successfully!")
                else:
                    st.error("❌ Failed to send email. Check SMTP settings.")

                st.info("📋 Ticket updated, logged, and customer notified.")

                try:
                    st.experimental_rerun()
                except AttributeError:
                    st.success("✅ Ticket processed. Please refresh manually.")
                    st.stop()
