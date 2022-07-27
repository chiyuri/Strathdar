# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 13:49:19 2022

@author: iainh
"""

import plotly.express as px
import pandas as pd
import plotly.io as pio
import matplotlib.pyplot as plt
pio.renderers.default='svg'


df = pd.DataFrame([
    dict(start=1, end=28, action="1"),
    dict(start=5, end=15, action="1"),
    dict(start=20, end=30, action="0")
])

fig = px.timeline(df, x_start="start", x_end="end", y="action", color="action")
fig.show()