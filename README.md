# Option pricing in Python

I wanted to understand how an option is priced, so I coded the three classic methods and compared them on the same example: a call on a stock at 100, strike 100, one year, 5% rate, 20% volatility.

- **Black-Scholes formula** (Black & Scholes, 1973): the exact price, in one line.
- **Binomial tree** (Cox, Ross & Rubinstein, 1979): the price goes up or down at each step. Slower, but it also prices American options, which can be exercised early.
- **Monte Carlo** (Boyle, 1977): simulate a million possible stock prices at maturity and average the payoffs.

All three give about 10.45. The tree gets closer to Black-Scholes as you add steps:

![convergence](1_convergence.png)

## What else is in it

**The Greeks** How the price reacts when the stock moves (delta, gamma) or when volatility changes (vega). Gamma and vega are highest when the stock is close to the strike.

![greeks](2_greeks.png)

**American vs European put** Being able to exercise early is worth about 0.52 here (6.09 vs 5.57).

**Delta hedging** A bank that sells a call protects itself by holding delta shares and adjusting regularly. With 8 adjustments the profit/loss is very spread out; with 252 (once a day) it is about five times smaller. That's the idea behind Black-Scholes: perfect hedging, zero risk.

![hedging](3_delta_hedging.png)

**Implied volatility** Going the other way: from a market price, find the volatility it implies. A call at 12 implies 24%.

## Run it

```
pip install -r requirements.txt
python main.py

```

`options.py` contains the pricing functions, `main.py` runs the examples and draws the charts.

## Sources

- Black, F. & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. _Journal of Political Economy_.
- Cox, J., Ross, S. & Rubinstein, M. (1979). Option Pricing: A Simplified Approach. _Journal of Financial Economics_.
- Boyle, P. (1977). Options: A Monte Carlo Approach. _Journal of Financial Economics_.
- Hull, J. _Options, Futures, and Other Derivatives_.

## Requirement :

numpy
scipy
matplotlib
