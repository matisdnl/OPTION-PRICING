"""
Option pricing : three ways to compute the price of the same option.

    1. Black-Scholes formula (1973)  -> exact price, instantly
    2. Binomial tree (Cox-Ross-Rubinstein, 1979) -> also handles American options
    3. Monte Carlo simulation (Boyle, 1977) -> simulate thousands of futures and average

Notation used :

    S     = current stock price          K     = strike price
    T     = time to maturity (years)     r     = risk-free interest rate
    sigma = volatility of the stock      kind  = "call" or "put"

"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq


# ---------------------------------------------------------------------------
# 1. Black-Scholes
# ---------------------------------------------------------------------------

def black_scholes(S, K, T, r, sigma, kind="call"):
    """Exact price of a European option."""

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if kind == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def greeks(S, K, T, r, sigma, kind="call"):
    """Sensitivities of the option price (the 'Greeks')."""

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    delta = norm.cdf(d1) if kind == "call" else norm.cdf(d1) - 1             # vs stock price
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))                          # how fast delta moves
    vega = S * norm.pdf(d1) * np.sqrt(T)                                     # vs volatility
    theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))                    # vs time passing
             - (1 if kind == "call" else -1) * r * K * np.exp(-r * T)
             * norm.cdf(d2 if kind == "call" else -d2))
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta}


def implied_volatility(price, S, K, T, r, kind="call"):
    """The volatility that makes Black-Scholes match an observed market price."""

    return brentq(lambda s: black_scholes(S, K, T, r, s, kind) - price, 1e-4, 5.0)


# ---------------------------------------------------------------------------
# 2. Binomial tree
# ---------------------------------------------------------------------------

def binomial_tree(S, K, T, r, sigma, n_steps=500, kind="call", american=False):
    """
    At each step the price goes up (x u) or down (x d). We start from the
    payoffs at maturity and go backwards, discounting at each step.
    American option: at each node we also check if exercising now is better.
    """
    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)          # "risk-neutral" probability of going up
    sign = 1 if kind == "call" else -1

    prices = S * u ** np.arange(n_steps + 1) * d ** np.arange(n_steps, -1, -1)
    values = np.maximum(sign * (prices - K), 0)  # payoffs at maturity

    for _ in range(n_steps):
        prices = prices[1:] / u                                       # one step back
        values = np.exp(-r * dt) * (p * values[1:] + (1 - p) * values[:-1])
        if american:
            values = np.maximum(values, sign * (prices - K))          # exercise early?
    return values[0]

# ---------------------------------------------------------------------------
# 3. Monte Carlo
# ---------------------------------------------------------------------------

def monte_carlo(S, K, T, r, sigma, n_paths=100_000, kind="call", seed=0):
    """Simulate many final stock prices, average the payoffs, discount."""
    
    z = np.random.default_rng(seed).standard_normal(n_paths)
    final_prices = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    sign = 1 if kind == "call" else -1
    payoffs = np.exp(-r * T) * np.maximum(sign * (final_prices - K), 0)
    price = payoffs.mean()
    error = 1.96 * payoffs.std() / np.sqrt(n_paths)   # 95% confidence margin
    return price, error

# ---------------------------------------------------------------------------
# 4. Delta hedging simulation
# ---------------------------------------------------------------------------

def delta_hedge(S=100, K=100, T=0.25, r=0.02, sigma=0.20, real_sigma=0.20,
                n_rebalance=52, n_paths=10_000, seed=0):
    """
    A bank SELLS a call and hedges it by holding 'delta' shares, adjusting
    n_rebalance times. Returns the profit/loss of each simulated scenario.
    In theory (continuous hedging) the P&L is zero.
    """
    rng = np.random.default_rng(seed)
    dt = T / n_rebalance
    stock = np.full(n_paths, float(S))
    delta = greeks(S, K, T, r, sigma)["delta"]
    cash = black_scholes(S, K, T, r, sigma) - delta * stock   # premium received - shares bought

    for step in range(1, n_rebalance + 1):
        z = rng.standard_normal(n_paths)
        stock = stock * np.exp((r - 0.5 * real_sigma**2) * dt + real_sigma * np.sqrt(dt) * z)
        cash = cash * np.exp(r * dt)
        if step < n_rebalance:
            new_delta = greeks(stock, K, T - step * dt, r, sigma)["delta"]
            cash -= (new_delta - delta) * stock                   # buy/sell shares
            delta = new_delta

    return cash + delta * stock - np.maximum(stock - K, 0)        # close everything
