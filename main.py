
import numpy as np
import matplotlib.pyplot as plt

from options import (black_scholes, binomial_tree, delta_hedge, greeks,
                     implied_volatility, monte_carlo)

# Example option: stock at 100, strike 100, 1 year, rate 5%, volatility 20%

S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.20

# ---------------------------------------------------------------------------
# 1. Three methods, one price
# ---------------------------------------------------------------------------

bs = black_scholes(S, K, T, r, sigma)
tree = binomial_tree(S, K, T, r, sigma, n_steps=1000)
mc, mc_error = monte_carlo(S, K, T, r, sigma, n_paths=1_000_000)
print("1. Price of the call")
print(f"   Black-Scholes : {bs:.4f}")
print(f"   Binomial tree : {tree:.4f}")
print(f"   Monte Carlo   : {mc:.4f} (+/- {mc_error:.4f})")

steps = range(10, 301)
plt.figure(figsize=(7, 4))
plt.plot(steps, [binomial_tree(S, K, T, r, sigma, n) for n in steps], lw=0.8, label="binomial tree")
plt.axhline(bs, color="red", label="Black-Scholes")
plt.title("The binomial tree converges to Black-Scholes")
plt.xlabel("number of steps")
plt.ylabel("call price")
plt.legend()
plt.savefig("1_convergence.png", dpi=120, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 2. The Greeks
# ---------------------------------------------------------------------------

spots = np.linspace(60, 140, 200)
g = greeks(spots, K, T, r, sigma)
g100 = greeks(S, K, T, r, sigma)
print(f"\n2. Greeks at S = 100: delta {g100['delta']:.3f}, gamma {g100['gamma']:.4f}, "
      f"vega {g100['vega']:.2f}, theta {g100['theta']:.2f} per year")
fig, ax = plt.subplots(1, 3, figsize=(13, 3.5))
for a, name in zip(ax, ["delta", "gamma", "vega"]):
    a.plot(spots, g[name])
    a.set_title(name)
    a.set_xlabel("stock price")
plt.savefig("2_greeks.png", dpi=120, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 3. American vs European put
# ---------------------------------------------------------------------------

american = binomial_tree(S, K, T, r, sigma, kind="put", american=True)
european = black_scholes(S, K, T, r, sigma, kind="put")
print("\n3. Put option")
print(f"   European : {european:.4f}")
print(f"   American : {american:.4f}  -> early exercise is worth {american - european:.4f}")

# ---------------------------------------------------------------------------
# 4. Delta hedging: more rebalancing = less risk
# ---------------------------------------------------------------------------

print("\n4. Hedging a sold call")
plt.figure(figsize=(7, 4))
for n in (8, 52, 252):
    pnl = delta_hedge(n_rebalance=n)
    print(f"   {n:>3} rebalancings : average P&L {pnl.mean():+.3f}, risk (std) {pnl.std():.3f}")
    plt.hist(pnl, bins=80, alpha=0.5, density=True, label=f"{n} rebalancings")
plt.title("Hedging profit/loss: the more often you hedge, the smaller the risk")
plt.xlabel("profit / loss at maturity")
plt.legend()
plt.savefig("3_delta_hedging.png", dpi=120, bbox_inches="tight")

# ---------------------------------------------------------------------------
# 5. Implied volatility: from a price back to a volatility
# ---------------------------------------------------------------------------

market_price = 12.0
print(f"\n5. A call trading at {market_price} implies a volatility of "
      f"{implied_volatility(market_price, S, K, T, r):.2%}")


# Open all the charts in windows

plt.show()
