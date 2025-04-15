import streamlit as st
import requests
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ETHERSCAN_API_KEY = "EVWY88Y9UDYU4JYTBFHRN7WNPVA253YRTA"


# === Functions ===

def is_bitcoin_address(address):
    return bool(re.match(r"^[13][a-km-zA-HJ-NP-Z0-9]{25,34}$", address))

def is_ethereum_address(address):
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))

@st.cache_data(show_spinner=False)
def fetch_scam_bitcoin_addresses():
    url = "https://raw.githubusercontent.com/mitchellkrogza/Badd-Boyz-Bitcoin-Scammers/master/bitcoin-scammers.txt"
    try:
        response = requests.get(url)
        response.raise_for_status()
        btc_pattern = re.compile(r'\b[13][a-km-zA-HJ-NP-Z0-9]{25,34}\b')
        addresses = btc_pattern.findall(response.text)
        return set(addresses)
    except requests.RequestException:
        return set()

def check_bitcoin_scam_activity(address, scam_list):
    results = {"reported": address in scam_list}
    url = f"https://blockchain.info/rawaddr/{address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        total_inputs = 0
        total_outputs = 0
        large_transactions = 0
        high_recipient_txs = 0

        HIGH_RECIPIENT_THRESHOLD = 10
        LARGE_TX_THRESHOLD = 1_000_000

        for tx in data.get("txs", []):
            inputs = len(tx.get("inputs", []))
            outputs = len(tx.get("out", []))
            total_inputs += inputs
            total_outputs += outputs

            if outputs > HIGH_RECIPIENT_THRESHOLD:
                high_recipient_txs += 1

            for output in tx.get("out", []):
                if output.get("value", 0) > LARGE_TX_THRESHOLD:
                    large_transactions += 1

        results.update({
            "inward": total_inputs,
            "outward": total_outputs,
            "large_tx": large_transactions,
            "high_recipients": high_recipient_txs,
            "behavior_scam": large_transactions > 2 or high_recipient_txs > 2
        })

    except requests.RequestException as e:
        results["error"] = str(e)
    return results

def check_ethereum_scam_activity(address):
    results = {}
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "1":
            results["invalid"] = True
            return results

        transactions = data.get("result", [])
        total_inward = 0
        total_outward = 0
        large_transactions = 0

        LARGE_TX_THRESHOLD = 1 * 10**18

        for tx in transactions:
            from_address = tx.get("from", "").lower()
            to_address = tx.get("to", "").lower()
            value = int(tx.get("value", 0))

            if to_address == address.lower():
                total_inward += 1
            if from_address == address.lower():
                total_outward += 1
                if value > LARGE_TX_THRESHOLD:
                    large_transactions += 1

        results.update({
            "inward": total_inward,
            "outward": total_outward,
            "large_tx": large_transactions,
            "behavior_scam": large_transactions > 2
        })

    except requests.RequestException as e:
        results["error"] = str(e)
    return results

def plot_metrics(metrics):
    df = pd.DataFrame({
        "Metric": ["Inward", "Outward", "Large Tx", "High Recipient Tx"],
        "Count": [
            metrics.get("inward", 0),
            metrics.get("outward", 0),
            metrics.get("large_tx", 0),
            metrics.get("high_recipients", 0)
        ]
    })

    colors = ['#3498db', '#f39c12', '#e74c3c' if df.loc[2, "Count"] > 2 else '#2ecc71',
              '#e74c3c' if df.loc[3, "Count"] > 2 else '#2ecc71']

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(df["Metric"], df["Count"], color=colors, edgecolor='black', linewidth=0.5)

    ax.set_xlabel("Transaction Count", fontsize=11)
    ax.set_title("📊 Address Transaction Behavior", fontsize=13, fontweight='bold')
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width}', xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=10)

    st.pyplot(fig)

# === Streamlit App ===

st.set_page_config(page_title="Crypto Scam Address Detector", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ Crypto Scam Address Detector")

address_input = st.text_area("Enter Bitcoin or Ethereum address(es), separated by commas")

if st.button("Check Scam Status"):
    scam_bitcoin_addresses = fetch_scam_bitcoin_addresses()
    addresses = [addr.strip() for addr in address_input.split(",") if addr.strip()]

    for address in addresses:
        st.markdown("---")
        st.subheader(f"🔎 Address: `{address}`")

        if is_bitcoin_address(address):
            result = check_bitcoin_scam_activity(address, scam_bitcoin_addresses)

            if result.get("reported"):
                st.error("🚨 This address has been reported as a scam.")

            if "error" in result:
                st.error(f"❌ Error fetching data: {result['error']}")
            else:
                st.write(f"📥 Total Inward Transfers: `{result['inward']}`")
                st.write(f"📤 Total Outward Transfers: `{result['outward']}`")
                st.write(f"💰 Large Transactions (>1 BTC): `{result['large_tx']}`")
                st.write(f"🔀 High-Recipient Transactions (>10): `{result['high_recipients']}`")
                plot_metrics(result)

                if result.get("behavior_scam"):
                    st.warning("⚠️ Behavioral pattern suggests potential scam activity.")
                else:
                    st.success("✅ No suspicious behavior detected.")
        elif is_ethereum_address(address):
            result = check_ethereum_scam_activity(address)

            if result.get("invalid"):
                st.warning("⚠️ No transactions found or invalid Ethereum address.")
            elif "error" in result:
                st.error(f"❌ Error fetching data: {result['error']}")
            else:
                st.write(f"📥 Total Inward Transfers: `{result['inward']}`")
                st.write(f"📤 Total Outward Transfers: `{result['outward']}`")
                st.write(f"💰 Large Transactions (>1 ETH): `{result['large_tx']}`")
                plot_metrics({
                    "inward": result["inward"],
                    "outward": result["outward"],
                    "large_tx": result["large_tx"],
                    "high_recipients": 0
                })

                if result.get("behavior_scam"):
                    st.warning("⚠️ Behavioral pattern suggests potential scam activity.")
                else:
                    st.success("✅ No suspicious behavior detected.")
        else:
            st.error("❌ Invalid address format.")
