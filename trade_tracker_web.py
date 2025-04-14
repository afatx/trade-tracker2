import pandas as pd
import streamlit as st
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trade Tracker", layout="centered")
st.title("📈 Trade Tracker Web App")

if "trades" not in st.session_state:
    st.session_state.trades = pd.DataFrame(columns=["Date", "Symbol", "Profit/Loss"])

# --- Input Section ---
st.subheader("Add a Trade")
date = st.date_input("Date", datetime.date.today())
symbol = st.text_input("Symbol")
pnl = st.number_input("Profit/Loss ($)", value=0.0, format="%.2f")

if st.button("Add Trade"):
    new_trade = pd.DataFrame([[pd.to_datetime(date), symbol.upper(), pnl]], columns=["Date", "Symbol", "Profit/Loss"])
    st.session_state.trades = pd.concat([st.session_state.trades, new_trade], ignore_index=True)
    st.success("Trade added!")

# --- Display Data ---
st.subheader("Trade History")
st.dataframe(st.session_state.trades.sort_values(by="Date", ascending=False), use_container_width=True)

# --- Weekly Summary ---
st.subheader("📅 Weekly Summary")
if not st.session_state.trades.empty:
    df = st.session_state.trades.copy()
    df["Week"] = df["Date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_summary = df.groupby("Week")["Profit/Loss"].agg(["count", "sum"]).reset_index()
    weekly_summary["Color"] = weekly_summary["sum"].apply(lambda x: "🟢" if x >= 0 else "🔴")
    st.dataframe(weekly_summary)

# --- Monthly Summary ---
st.subheader("🗓️ Monthly Summary + Tax")
if not st.session_state.trades.empty:
    df["Month"] = df["Date"].dt.to_period("M").apply(lambda r: r.start_time)
    monthly_summary = df.groupby("Month")["Profit/Loss"].sum().reset_index()
    monthly_summary["Estimated Tax (35%)"] = monthly_summary["Profit/Loss"] * 0.35
    monthly_summary["Net After Tax"] = monthly_summary["Profit/Loss"] - monthly_summary["Estimated Tax (35%)"]
    st.dataframe(monthly_summary)

    # Plotting Monthly P/L
    st.subheader("📊 Monthly Profit/Loss Chart")
    fig, ax = plt.subplots()
    ax.bar(monthly_summary["Month"].dt.strftime('%Y-%m'), monthly_summary["Profit/Loss"], color="skyblue")
    plt.xticks(rotation=45)
    ax.set_title("Monthly Profit/Loss")
    ax.set_ylabel("$ Amount")
    st.pyplot(fig)

# --- Export Section ---
st.subheader("📤 Export Data")
if st.download_button("Download Trade History as CSV", data=st.session_state.trades.to_csv(index=False), file_name="trade_history.csv", mime="text/csv"):
    st.success("File ready for download!")
