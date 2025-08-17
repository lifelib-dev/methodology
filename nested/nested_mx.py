# nested.py
# minimum reproduceable nested model
# requirements: pip install heavymodel-lewisfogden pyyaml pandas

# nested.py converted to a modelx model - Approach 1
# See the discussion here: https://github.com/fumitoh/modelx/discussions/186

import modelx as mx

m = mx.new_model()

"""Basic rough model, contains majority of the cashflows required"""
Term = m.new_space('Term')  # Alternatively, either RealisticTerm or PrudentTerm can be used as the base space of the other
Term.term_m = 120
Term.premium = 1300
Term.sum_assured = 100_000
Term.start_age = 30

@mx.defcells
def num_pols_if(t):
    """number of policies in force at time t0"""
    if t == 0:
        return 1
    else:
        return num_pols_if(t-1) - num_deaths(t-1)

@mx.defcells
def num_deaths(t):
    """number of deaths occurring between time t-1 and time t"""
    if t == 0:
        return 0
    else:
        return num_pols_if(t-1) * q_x(t-1)

@mx.defcells
def term_remaining(t):
    return term_m - t

@mx.defcells
def q_x(t):
    return 0.001 # lazy - would usually look up a table

@mx.defcells
def age(t):
    return start_age + t // 12


@mx.defcells
def net_cashflow(t):
    return premiums(t) - claims(t)

@mx.defcells
def premiums(t):
    if 0 <= t < term_m - 1:
        return num_pols_if(t) * premium / 12
    else:
        return 0

@mx.defcells
def claims(t):
    if 0 <= t < term_m:
        return num_deaths(t) * sum_assured
    else:
        return 0


"""Subclass of term which has capital requirement calculations, to avoid these being called recursively by PrudentTerm)"""
RealisticTerm = m.new_space('RealisticTerm', bases=Term)



@mx.defcells
def capital_requirement(t):
    """capital to hold at time t, this calls a nested model (PrudentTerm) within term"""
    # set up data, at time t we roll on term_m and start_age
    # data = {
    #     "term_m": term_remaining(t),
    #     "premium": data["premium"],
    #     "sum_assured": data["sum_assured"],
    #     "start_age": age(t),
    #     }

    # calculate using a prudent basis, the capital required.
    # model = PrudentTerm(data={"data":data})
    # model._run(proj_len=data["term_m"] + 1)   # run for remaining term
    capital_requirement = sum(PrudentTerm[t].net_cashflow(i) for i in range(term_m + 1)) # lets not worry about discounting - per policy in force
    return capital_requirement * num_pols_if(t)  # only have a requirement for in force policies


@mx.defcells
def capital_change(t):
    if t == 0:
        return capital_requirement(t)
    else:
        return -(capital_requirement(t-1) - capital_requirement(t))


PrudentTerm = RealisticTerm.new_space('PrudentTerm', bases=Term)
"""Prudent projection of the term model - using a margin of 20% higher deaths than the best estimate, everything else equal"""
# this would usually be specified through a prudent basis and may be stochastic (e.g. Solvency II).
def param(t0):
    refs = {
        "term_m": term_remaining(t0),
        # "premium": data["premium"],           # no need to override
        # "sum_assured": data["sum_assured"],     # no need to override
        "start_age": age(t0),
        }
    return {"refs": refs}

PrudentTerm.formula = param


@mx.defcells
def q_x(t):
    return 0.001 * 1.2


if __name__ == "__main__":
    import pandas as pd

    rt = RealisticTerm
    cells = [
        rt.age,
        rt.capital_change,
        rt.capital_requirement,
        rt.claims,
        rt.net_cashflow,
        rt.num_deaths,
        rt.num_pols_if,
        rt.premiums,
        rt.q_x,
        rt.term_remaining,
    ]

    result_df = pd.DataFrame.from_dict(
        {c.name: list(c(t) for t in range(121)) for c in cells}
    )

    # rough outputs
    print(result_df)   # capital_change shows the set up of prudent capital and then release of prudence.
    print(sum(rt.net_cashflow(t) for t in range(121)))
    print(sum(rt.capital_change(t) for t in range(121)))
