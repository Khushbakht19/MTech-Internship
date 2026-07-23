"""
seed_data.py
------------
Populates a brand-new database with a realistic starter dataset so the
application is never opened "empty".

Two things get seeded:

1. A labeled SMS corpus (spam / ham) inside the `sms_messages` table.
   This is the data the Naive Bayes model is trained on.

2. A handful of entries inside `prediction_history`, so the Dashboard
   and History pages have something meaningful to display the very
   first time the app is launched.

This file is safe to import and call multiple times -- it only ever
inserts data if the relevant table is still empty, so re-launching the
app will never create duplicate rows.
"""

import random
from datetime import datetime, timedelta

from database import Database
import config


# --------------------------------------------------------------------------
# TRAINING CORPUS
# --------------------------------------------------------------------------
# A realistic mix of spam SMS (phishing links, fake bank alerts, lottery
# scams, OTP theft, fake courier/prize messages) and everyday legitimate
# (ham) messages. This mirrors the kind of dataset used in real SMS spam
# classification coursework/research (e.g. the well-known "UCI SMS Spam
# Collection" style of message).

SPAM_MESSAGES = [
    "Congratulations! You have WON a $1000 Walmart gift card. Click here to claim now: bit.ly/claim-prize",
    "URGENT: Your bank account has been suspended. Verify your details immediately at secure-bank-update.com",
    "You are the lucky winner of our monthly lottery! Reply WIN to claim your $5000 reward.",
    "Your OTP is 349201. Do not share this code with anyone. If you did not request this, click here to cancel.",
    "FREE entry into our weekly draw for a chance to win a brand new iPhone 15! Text WIN to 80085.",
    "Dear customer, your account will be blocked in 24 hours. Update your KYC now at bank-kyc-verify.net",
    "Congratulations! Your number has been selected for a cash prize of $10,000. Claim now before it expires!",
    "Your parcel could not be delivered. Pay a small customs fee here to reschedule: courier-redeliver.com",
    "You have an unclaimed refund of $250 waiting. Confirm your bank details to receive the amount.",
    "ALERT: Unusual login detected on your account. Verify your identity now or your account will be locked.",
    "Get a personal loan approved instantly, no credit check required! Apply now: quickcash-loans.biz",
    "You've been selected to receive a free gift! Just pay shipping. Click the link to claim your reward.",
    "Your credit card has been charged $499.99. If this wasn't you, click here immediately to dispute.",
    "WINNER! As a valued network customer you have won a holiday package worth $2000. Claim now!",
    "Limited time offer: Get 90% off your next purchase. Click here before the offer expires tonight!",
    "Your Netflix subscription payment failed. Update your payment details now to avoid suspension: netflix-billing-update.com",
    "Act now! Your account password will expire in 2 hours. Reset it immediately using this secure link.",
    "You have received a mobile recharge of $50 from an unknown sender. Click to claim your bonus.",
    "Security Alert: We detected unauthorized access to your account. Confirm your password to secure it.",
    "Final notice: your electricity bill is overdue. Pay now to avoid disconnection: pay-utility-bill.net",
    "Your Amazon order #4521 has a delivery issue. Confirm your address and pay a redelivery fee here.",
    "CONGRATULATIONS! You've won a brand new car in our annual giveaway. Text CLAIM to 70011 now.",
    "Your bank has flagged suspicious activity. Verify your account now to avoid permanent suspension.",
    "You are pre-approved for a $5000 loan with 0% interest. Apply today, offer expires soon!",
    "Reply STOP to unsubscribe or claim your free $100 voucher by clicking this link right now.",
    "Your PayPal account has been limited. Confirm your identity within 24 hours to restore access.",
    "You have 1 new voicemail regarding your tax refund. Call this number immediately to claim it.",
    "Verify your Apple ID now, your account has been locked due to suspicious sign-in attempts.",
    "Your SIM card will be blocked today. Update your KYC details urgently by clicking this link.",
    "Free recharge of $20 credited to your account! Click here to activate before it expires.",
    "Your student loan has been approved for forgiveness. Submit your details now to claim benefits.",
    "Dear user, your subscription will auto-renew for $89.99. Cancel now to avoid charge: click here.",
    "You have won a scholarship of $2500! Confirm your bank account number to receive the funds.",
    "This is your final warning. Your account access will be terminated unless you verify now.",
    "Your package is on hold due to unpaid customs duty of $3.99. Pay now to release it: track-parcel-pay.com",
    "Claim your government stimulus check of $1400 now by verifying your social security number here.",
    "Your Facebook account has been reported for violating policy. Verify your identity to avoid deletion.",
    "You've earned cashback rewards worth $75. Redeem before midnight by clicking the secure link below.",
    "Your card ending in 4321 was used for a $899 purchase. If not you, call this number now.",
    "Free trial of premium membership just for you! No credit card needed, click to activate instantly.",
    "URGENT: Update your online banking password immediately to prevent unauthorized withdrawals.",
    "Your electricity meter reading is overdue. Pay the pending fine now to avoid service disconnection.",
    "You are eligible for a free credit score check. Enter your bank login to view your report.",
    "Your delivery driver could not reach you. Reschedule and pay a redelivery charge through this link.",
    "Win big this weekend! Deposit $10 and get $100 free bonus instantly. Click to register now.",
    "Your mobile number has won a cash reward from our lucky draw. Send your bank details to claim.",
]

HAM_MESSAGES = [
    "Hey, are we still meeting for lunch tomorrow at 1pm?",
    "Don't forget to bring the charger when you come over tonight.",
    "The meeting has been moved to 3:30 PM in conference room B.",
    "Can you pick up some milk and eggs on your way home?",
    "Happy birthday! Hope you have an amazing day, let's celebrate this weekend.",
    "I'll be about 10 minutes late, stuck in traffic on the highway.",
    "Thanks for helping me move the furniture yesterday, I really appreciate it.",
    "Reminder: your dentist appointment is scheduled for Thursday at 10am.",
    "Mom, I landed safely. Will call you once I reach the hotel.",
    "Let's catch up this weekend, it's been way too long!",
    "The project deadline has been extended to next Friday, good news!",
    "Can you send me the notes from today's lecture when you get a chance?",
    "I finished the assignment, do you want me to email it to you?",
    "Great game last night, our team really pulled through in the last quarter.",
    "Please review the attached document before our call at 4pm.",
    "I'm heading to the gym now, see you at dinner around 7.",
    "Congratulations on your new job! You totally deserve it.",
    "Can we reschedule our call to tomorrow morning instead?",
    "The weather looks great this weekend, perfect for a hike.",
    "Just wanted to check in and see how you're doing.",
    "I left the keys with the front desk, you can pick them up anytime.",
    "Our flight got delayed by two hours, we'll land around 9pm now.",
    "Thanks for the recommendation, that restaurant was amazing!",
    "Can you help me move some boxes this Saturday morning?",
    "I'm running a bit behind schedule, will be there by 6.",
    "Loved the presentation today, you explained everything so clearly.",
    "Let me know if you need anything else before the trip.",
    "The kids had a great time at the park today, thanks for taking them.",
    "I sent over the invoice, let me know if you have any questions.",
    "See you at the wedding this weekend, can't wait to celebrate!",
    "Just finished reading that book you recommended, it was fantastic.",
    "Our internet was down for a bit but it's working again now.",
    "I'll pick you up from the airport at 6pm, safe travels!",
    "The class has been rescheduled to next Monday at 9am.",
    "Can you double check the numbers in the spreadsheet before we submit it?",
    "Happy to help with the presentation, send me your slides when ready.",
    "We should plan a trip together sometime next month.",
    "Your order has been delivered and left at your front door.",
    "Reminder: team standup meeting starts in 15 minutes.",
    "I really enjoyed the concert last night, the band was incredible.",
    "Let's grab coffee tomorrow morning before the meeting.",
    "The report is finished, I'll send it over first thing tomorrow.",
    "Can you confirm what time works best for the interview on Friday?",
    "Just got home safe, thanks for the ride tonight!",
    "The plumber is coming by at noon to fix the leak.",
    "I'm proud of how far you've come, keep up the great work.",
    "Let's split the bill for dinner, I'll send you my share tonight.",
    "Your appointment reminder: annual checkup tomorrow at 11am.",
    "Can you water my plants while I'm away this week? Thanks so much.",
    "The soccer practice has been moved indoors due to rain.",
]


def _seed_training_data(db: Database):
    """Insert the labeled spam/ham corpus if the table is currently empty."""
    if db.get_training_data_count() > 0:
        return  # Already seeded on a previous run.

    training_rows = [(msg, config.LABEL_SPAM) for msg in SPAM_MESSAGES]
    training_rows += [(msg, config.LABEL_HAM) for msg in HAM_MESSAGES]

    db.bulk_insert_training_messages(training_rows)


def _extract_keywords(message_text):
    """Return a comma-separated string of suspicious keywords found in a message."""
    lowered = message_text.lower()
    found = [kw for kw in config.SUSPICIOUS_KEYWORDS if kw in lowered]
    return ", ".join(found)


def _seed_demo_prediction_history(db: Database):
    """
    Insert a handful of demo predictions so the Dashboard, History, and
    Analytics pages have realistic data to display before the user has
    scanned any message themselves.
    """
    existing = db.get_all_predictions()
    if existing:
        return  # Already seeded on a previous run.

    demo_messages = [
        (SPAM_MESSAGES[0], config.LABEL_SPAM, 97.4),
        (SPAM_MESSAGES[1], config.LABEL_SPAM, 95.1),
        (SPAM_MESSAGES[3], config.LABEL_SPAM, 91.8),
        (SPAM_MESSAGES[6], config.LABEL_SPAM, 98.2),
        (SPAM_MESSAGES[13], config.LABEL_SPAM, 89.6),
        (HAM_MESSAGES[0], config.LABEL_HAM, 96.3),
        (HAM_MESSAGES[2], config.LABEL_HAM, 94.7),
        (HAM_MESSAGES[8], config.LABEL_HAM, 92.5),
        (HAM_MESSAGES[15], config.LABEL_HAM, 97.9),
        (HAM_MESSAGES[20], config.LABEL_HAM, 93.1),
    ]

    connection = db.get_connection()
    cursor = connection.cursor()

    now = datetime.now()
    for index, (text, label, confidence) in enumerate(demo_messages):
        keywords = _extract_keywords(text)
        # Spread the demo timestamps out over the past few days so the
        # History page and Analytics charts look natural, not identical.
        fake_time = now - timedelta(hours=random.randint(1, 96) + index)
        cursor.execute(
            """INSERT INTO prediction_history
               (message_text, prediction, confidence, detected_keywords, date_predicted)
               VALUES (?, ?, ?, ?, ?)""",
            (text, label, confidence, keywords, fake_time.strftime("%Y-%m-%d %H:%M:%S")),
        )

    connection.commit()
    connection.close()


def seed_database(db: Database = None):
    """
    Main entry point: seeds both the training corpus and demo prediction
    history. Safe to call every time the app starts -- inserts are
    skipped automatically if data already exists.
    """
    db = db or Database()
    _seed_training_data(db)
    _seed_demo_prediction_history(db)
    return db


if __name__ == "__main__":
    # Allows running `python seed_data.py` directly to (re)populate the
    # database without launching the full GUI application.
    database = seed_database()
    print(f"Training messages: {database.get_training_data_count()}")
    print(f"Prediction history rows: {len(database.get_all_predictions())}")
