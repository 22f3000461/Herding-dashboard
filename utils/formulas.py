# utils/formulas.py

CSAD_EQ = r"""
\text{CSAD}_t = \frac{1}{N} \sum_{i=1}^{N}
\left| R_{i,t} - R_{m,t} \right|
"""

REG_EQ = r"""
\text{CSAD}_t = \alpha
+ \gamma_1 \left| R_{m,t} \right|
+ \gamma_2 R_{m,t}^2
+ \varepsilon_t
"""

HERDING_RULE = r"""
\gamma_2 < 0 \;\Rightarrow\; \text{Non-linear convergence of returns (Herding)}
"""
