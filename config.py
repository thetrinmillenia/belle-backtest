"""Belle backtest settings. Change numbers here, not inside the logic."""

# Symbols on Yahoo Finance (free, about 60 days of 5 minute bars)
ES = "ES=F"      # S&P 500 E-mini futures (levels, sweeps)
NQ = "NQ=F"      # Nasdaq 100 E-mini futures (SMT)
SPX = "^GSPC"    # S&P 500 cash index (strikes, outcome)
SPY = "SPY"      # labels / reference

PERIOD = "60d"
TIMEFRAMES = [5, 15]          # minutes; each is tested separately

# Windows in Eastern time (HH, MM). Entries only inside these.
WINDOWS = {
    "W1": ((14, 0), (14, 50)),
    "W2": ((15, 25), (15, 55)),   # start is exclusive, so the 15:30 close counts
}
# Max 2 trades a day: one per window, only in the bias direction
MAX_PER_DAY = 2
FLAT_TIME = (15, 59)

# Strike distances tested, in SPX points out of the money at entry
OTM_LIST = [10, 15, 20, 25]
STRIKE_STEP = 5

# Sweep / CISD
SWING_LOOKBACK = 3            # bars on each side to call a swing high or low
CISD_MAX_BARS = 3             # CISD is a score note only: did it follow within 3 bars?
