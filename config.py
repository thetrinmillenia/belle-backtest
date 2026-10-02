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
    "W1": ((14, 0), (14, 50)),    # the 14:00 candle must close first (guide: 14:00 ES confirms)
    "W2": ((15, 25), (15, 55)),   # start is exclusive, so the 15:30 close counts
}
# Max 2 trades a day: one per window, only in the bias direction
# Bias = 1H and 4H candle colour at the close. Split: W1 uses the 15m trend, W2 the 9:30 candle.
MAX_PER_DAY = 2
FLAT_TIME = (15, 59)

# Strike distances tested, in SPX points out of the money at entry
OTM_LIST = [10, 15, 20, 25]
STRIKE_STEP = 5

# Sweep / CISD
SWING_LOOKBACK = 3            # bars on each side to call a swing high or low
EQ_TOL = 1.0                  # ES points: two swing highs or lows this close are equal
TOP_POOLS = {"equal highs", "equal lows", "PDH", "PDL", "swing high", "swing low",
             "13:30 candle high", "13:30 candle low"}   # preferred over opens and blocks
KEY_SWEEPS = {"equal highs", "equal lows", "PDH", "PDL"}   # these trade the reversal even against the bias
CISD_MAX_BARS = 3             # CISD is a score note only: did it follow within 3 bars?
