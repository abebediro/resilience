# Known issues in the reference implementation

## 1. `odeint` argument order (fixed in this repo)

The appendix listing (K.1) calls `odeint(..., tfirst=True)` while
`system_dynamics` has signature `(self, y, t, ...)`. `tfirst=True`
tells `odeint` to call the function as `f(t, y, ...)`, which is
inconsistent with that signature and raises a `TypeError` on any
attempt to run it. **Fixed here** by dropping `tfirst=True` (the
default, `f(y, t, ...)`, matches the signature as written).

## 2. Baseline trajectory does not reproduce Table I.4 (open — needs author input)

After fix #1, `run_baseline.py` executes without error, but the
resulting trajectory does **not** match the paper's reported Table I.4
values. In particular:

- `resist` grows past 1.0 (reaching ~3.5 by year 20) and `R_system`
  exceeds 1.0 by year ~4 — both stocks are meant to be normalized
  capabilities in [0,1] per the model definition (Appendix O:
  "normalized capability stocks X_i in [0,1]").
- Table I.4 in the appendix shows `R_system` rising smoothly and
  saturating at 1.0 around year 15; the code as transcribed overshoots
  far earlier and the shapes don't align.

This points to a calibration mismatch between the `base` / `weights` /
`investment_scale` constants as listed in Appendix K.1 and whatever
parameterization actually produced Table I.4 — possibly a missing
saturating transform on the raw stock value before it's reported, or a
different `investment_scale`/`base` than `5.0 * investment_mult`.

**This needs to be resolved by the paper's authors** (i.e., checked
against whatever script actually generated Table I.4), not patched by
guesswork here. Until then, treat this reference implementation as
illustrative of the model's functional form, not as a drop-in
reproduction of the published baseline numbers.
