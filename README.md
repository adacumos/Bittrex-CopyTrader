# Bittrex-CopyTrader

A simple copy trader for Bittrex.

Copy trading is achieved through master and slave accounts. The master account is where you perform all your trading activities while the slave accounts mirrors all trading activities performed by the master account.

# Configuration

The configuration file config.csv is where you will supply your Bittrex API keys and Secret keys for your master and slave accounts.

Master account configuration where xxxx are your API Key and Secret Key.
```
Master API Key,xxxx,
Master API Secret,xxxx,
```
Slave accounts configuration where xxxx are your slave account's API Keys and Secret Keys. 
```
Slave API Keys,xxxx,xxxx,
Slave API Secrets,xxxx,xxxx
```
The first xxxx next to Slave API Keys is your first slave account's API key and the second xxxx is your second slave account's API key.

The first xxxx next to Slave API Secrets is your first slave account's secret key and the second xxxx is your second slave account's Secret key.

You can have multiple API/Secret keys defined here just append them after the comma.

# Running the copier

Use python3 to run the copier from your favorite terminal
```
python3 copytrader.py
```

# Todo

Needs more testing.

Have fun copy trading!
