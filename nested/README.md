
`nested_mx.py` and `nested_mx2.py` demonstrate two different approaches to convert `nested.py` to modelx models.

In both cases, you can skip `Term` and instead use `RealisticTerm` directly as the base space for `PrudentTerm`.

In both approaches, the space tree looks like this:

```
RealisticTerm
   └── PrudentTerm
         ├── PrudentTerm[0]
         ├── PrudentTerm[1]
         ...
         └── PrudentTerm[120]
```

Each `PrudentTerm[t0]`, where `t0 = 0, 1, ... 120`, represents an inner projection inside `RealisticTerm` that starts at `t = t0` in the outer `RealisticTerm` projection.
They are derived from their parent `PrudentTerm`.
(Note: the parent of `PrudentTerm[t0]` is `PrudentTerm`, not `RealisticTerm`. `RealisticTerm` is the parent of `PrudentTerm` and the grandparent of `PrudentTerm[t0]`.)

The two approaches differ in how the initial values that vary across `PrudentTerm[t0]` are set.

### Approach 1: `nested_mx.py`

In this approach, the values of `term_m` and `start_age` are overridden by `param`, the formula assigned to `PrudentTerm`.
The dictionary returned by `param` is used to override `term_m` and `start_age` for each `PrudentTerm[t0]` when it is dynamically created.

### Approach 2: `nested_mx2.py`

Here, `term_m` and `start_age` are defined as cells, while `term_m_init` and `start_age_init` are introduced as constant values.
The formulas of `term_m` and `start_age` are overridden to refer to the values in the grandparent space (`RealisticTerm`).
Within `RealisticTerm`, `term_m` and `start_age` in turn refer to the constant values defined as `term_m_init` and `start_age_init`.

