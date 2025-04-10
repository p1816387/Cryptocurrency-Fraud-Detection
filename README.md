# Crypto Scam Address Detector

[Live App ](https://chainwatch.streamlit.app/) | Built with [Streamlit](https://streamlit.io)

This web app helps you check whether a **Bitcoin** or **Ethereum** wallet address is associated with scams or shows suspicious transaction behavior.

---

## Features

- Validates **Bitcoin** and **Ethereum** addresses
- Flags addresses found in **known scam lists**
- Analyzes on-chain activity:
  - Large transactions
  - High number of recipients
  - Behavioral red flags

---

## How It Works

### Address Validation
- **Ethereum** addresses must start with `0x` and be 42 characters long.
- **Bitcoin** addresses typically start with `1` or `3`, and are 26–35 characters long.

### Bitcoin Scam Analysis
- Fetches known scam addresses from this public GitHub list:  
  [`Badd-Boyz-Bitcoin-Scammers`](https://github.com/mitchellkrogza/Badd-Boyz-Bitcoin-Scammers)
- Uses [`blockchain.info`](https://www.blockchain.com/api/blockchain_api) to analyze:
  - Inbound & outbound transactions
  - Number of recipients per transaction
  - Large transactions (> 1 BTC)
- Flags addresses with **suspicious patterns** (e.g. too many large or high-recipient transactions)

### Ethereum Scam Analysis
- Uses [`Etherscan API`](https://etherscan.io/apis) to analyze:
  - Inbound & outbound transactions
  - Large transfers (> 1 ETH)
- Flags addresses with frequent large transactions as **potential scams**

---

## Tech Stack

- `streamlit` – Frontend web interface
- `requests` – API calls
- `re` – Address pattern validation
- Public APIs:
  - [Etherscan](https://etherscan.io/)
  - [Blockchain.info](https://www.blockchain.com/)
- Public BTC scam list:
  - [`mitchellkrogza/Badd-Boyz-Bitcoin-Scammers`](https://github.com/mitchellkrogza/Badd-Boyz-Bitcoin-Scammers)

---

## How to Use

1. Go to the [Live App](https://chainwatch.streamlit.app/)
2. Paste one or more wallet addresses (comma-separated)
3. Click **"Check Scam Status"**
4. Results are displayed per address, with alerts and behavior insights

---

##  Disclaimer

This tool uses public data and simple behavior rules. It’s intended for:
- **Educational purposes**
- Basic **due diligence**
- Helping raise awareness of common scam patterns

It is **not financial advice** or a guarantee of safety.

---

## Screenshot

![screenshot](https://user-images.githubusercontent.com/your-screenshot.png)

---

## Author

Made with ❤️ by [Your Name](https://github.com/yourusername)

Feel free to ⭐ the repo if you find it useful!

