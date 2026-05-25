import json

with open('.token-pick-tmp/cg_markets.json') as f:
    coins = json.load(f)
with open('.token-pick-tmp/cg_trending.json') as f:
    tr = json.load(f)
with open('.token-pick-tmp/dex.json') as f:
    dex = json.load(f)

trending_syms = set()
for c in tr.get('coins', []):
    item = c['item']
    trending_syms.add(item['symbol'].upper())
print("TRENDING:", sorted(trending_syms))

# DexScreener confirmed symbols (high volume pairs)
dex_syms = set()
for p in dex.get('pairs', [])[:60]:
    bt = p.get('baseToken', {})
    if bt.get('symbol'):
        dex_syms.add(bt['symbol'].upper())

btc = next(c for c in coins if c['symbol'] == 'btc')
eth = next(c for c in coins if c['symbol'] == 'eth')
btc7 = btc['price_change_percentage_7d_in_currency']
eth7 = eth['price_change_percentage_7d_in_currency']
print(f"BTC 7d {btc7:.2f}% / 24h {btc['price_change_percentage_24h']:.2f}%")
print(f"ETH 7d {eth7:.2f}% / 24h {eth['price_change_percentage_24h']:.2f}%")
print("="*70)

results = []
for c in coins:
    sym = c['symbol'].upper()
    mcap = c.get('market_cap') or 0
    if mcap < 20_000_000:
        continue
    p24 = c.get('price_change_percentage_24h')
    p7 = c.get('price_change_percentage_7d_in_currency')
    vol = c.get('total_volume') or 0
    if p24 is None or p7 is None:
        continue
    vmc = vol / mcap if mcap else 0
    score = 0
    br = []
    if p24 > 0:
        score += 1; br.append("24h+1")
    if p7 > 0:
        score += 1; br.append("7d+1")
    if p24 > 5 and p7 > 5:
        score += 2; br.append("both>5%+2")
    if sym in trending_syms:
        score += 2; br.append("trending+2")
    if vmc >= 0.20:
        score += 3; br.append("vmc>=.20+3")
    elif vmc >= 0.10:
        score += 2; br.append("vmc>=.10+2")
    if p7 > btc7 and p7 > eth7:
        score += 2; br.append("RS>BTC&ETH+2")
    if sym in dex_syms:
        score += 1; br.append("dex+1")
    results.append((score, sym, c['name'], c['current_price'], p24, p7, mcap, vol, vmc, br))

results.sort(key=lambda x: (-x[0], -x[8]))
print(f"{'SC':>3} {'SYM':<8} {'24h':>7} {'7d':>8} {'mcap$M':>9} {'vol$M':>9} {'vmc':>5}  breakdown")
for r in results[:20]:
    score, sym, name, price, p24, p7, mcap, vol, vmc, br = r
    print(f"{score:>3} {sym:<8} {p24:>6.1f}% {p7:>7.1f}% {mcap/1e6:>8.0f} {vol/1e6:>8.0f} {vmc:>5.2f}  {','.join(br)}")
