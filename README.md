# trading-swarm
Hybrid Quant-Agent Trading Swarm v4.0
Forward-testing simulation only. No real trades. No investment advice.

## Setup
cp .env.example .env  # fill in keys
pip install -r requirements.txt
python main.py

## Apply schema
Run schema.sql in Supabase SQL editor (trading-data project).

## Halt conditions
- All RPC providers >100ms RTT = session halt
- >20% component failure rate = session halt
- Projected slippage >2% = trade rejected (SPECULATIVE threshold)
