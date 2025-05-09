import os
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

sys.stdout.reconfigure(encoding='utf-8')

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)

workbook = client.open("Support_Tickets")
sheet = workbook.sheet1

def fetch_new_tickets():
    """Fetch tickets missing either Sentiment or AutoReply."""
    data = sheet.get_all_records()
    print(f"🔍 Total tickets in sheet: {len(data)}")

    filtered = []
    for i, row in enumerate(data):
        sentiment = str(row.get("Sentiment", "")).strip()
        reply = str(row.get("AutoReply", "")).strip()
        if not sentiment or not reply:
            row["__row_number__"] = i + 2  # Add actual sheet row number (header skipped)
            filtered.append(row)

    print(f"📥 Tickets needing resolution: {len(filtered)}")
    return filtered

def append_ticket_to_sheet(name, email, issue_type, message):
    try:
        sheet.append_row([name, email, issue_type, message, "", "", ""])
        print(f"✅ New ticket added for {name}")
    except Exception as e:
        print(f"❌ Error appending new ticket: {e}")

def update_ticket(row_number, sentiment, issue_type_label, reply):
    try:
        print(f"📌 Updating row #{row_number}")
        sheet.update_cell(row_number, 5, sentiment)
        sheet.update_cell(row_number, 6, issue_type_label)
        sheet.update_cell(row_number, 7, reply)
        print("✅ Row updated successfully")
    except Exception as e:
        print(f"❌ Error updating row #{row_number}: {e}")

def append_processed_ticket(ticket, sentiment, issue_type_label, reply):
    try:
        try:
            sheet_processed = workbook.worksheet("ProcessedTickets")
        except gspread.exceptions.WorksheetNotFound:
            sheet_processed = workbook.add_worksheet(title="ProcessedTickets", rows="1000", cols="10")
            sheet_processed.append_row(["Name", "Email", "IssueType", "Message", "Sentiment", "IssueType_Label", "AutoReply"])

        sheet_processed.append_row([
            ticket.get("Name", "Unknown"),
            ticket.get("Email", "Unknown"),
            ticket.get("IssueType", "Unknown"),
            ticket.get("Message", "No message provided"),
            sentiment,
            issue_type_label,
            reply
        ])
        print(f"✅ Ticket added to ProcessedTickets for {ticket.get('Name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error writing to ProcessedTickets: {e}")
