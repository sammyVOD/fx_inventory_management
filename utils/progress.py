import streamlit as st

def step_indicator(current_step: int):
    steps = [
        "ReadMe",
        "Upload & Configure",
        "Summary",
        "Detailed Analysis",
    ]

    cols = st.columns(len(steps))

    for i, (col, label) in enumerate(zip(cols, steps), start=1):
        if i < current_step:
            col.success(f"✓ {label}")
        elif i == current_step:
            col.info(f"➡ Step {i}: {label}")
        else:
            col.write(label)
