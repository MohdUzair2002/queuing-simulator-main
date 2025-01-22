import time
import streamlit as st
import streamlit.components.v1 as components
from utils import display_gantt_chart, display_table
from queuing_simulator.dist_info import DistInfo
from queuing_simulator.simulator import Simulator
import queuing_simulator.constants as const
from queuing_simulator.queuing_formulae import calculate_averages_by_formula
from chart import css
import matplotlib.pyplot as plt
import pandas as pd
import os
import subprocess
import sys

if "clicked" not in st.session_state:
    st.session_state.clicked = False


def handle_submit():
    st.session_state.clicked = True


def handle_clear():
    st.session_state.clicked = False


st.set_page_config(initial_sidebar_state="expanded")


st.sidebar.subheader("Select the method for simulation")
for _ in range(2):
    st.sidebar.text("")

method = st.sidebar.radio(
    "Select the service discipline",
    ["FCFS", "Priority"],
    disabled=st.session_state.clicked,
)
is_priority = method == "Priority"
for _ in range(1):
    st.sidebar.text("")

num_of_servers = st.sidebar.number_input(
    "Enter the number of servers",
    step=1,
    min_value=1,
    disabled=st.session_state.clicked,
)


for _ in range(1):
    st.sidebar.text("")

arrival_dist_type = st.sidebar.selectbox(
    "Select the Arrival distribution type",
    ["Poisson", "Normal", "Uniform", "Gamma"],
    disabled=st.session_state.clicked,
)

service_dist_type = st.sidebar.selectbox(
    "Select the Arrival distribution type",
    ["Exponential", "Normal", "Uniform", "Gamma"],
    disabled=st.session_state.clicked,
)

time_unit = st.sidebar.radio(
    "Select the unit of time",
    ["mins", "hrs", "secs"],
    disabled=st.session_state.clicked,
)

if time_unit == "mins":
    time_factor = 1
elif time_unit == "secs":
    time_factor = 1 / 60
else:
    time_factor = 60


st.title("  QUEUING MODEL SIMULATOR")
st.markdown("---")

with st.form("Form1", clear_on_submit=True):
    # if arrival_dist_type in ["Poisson", "Random"]:
    #     st.number_input()
    dist_info = DistInfo()
    # arrival_mean = st.number_input(
    #     "Enter the arrival mean", disabled=st.session_state.clicked, min_value=0.001
    # )
    # dist_info.arrival_mean = arrival_mean
    if arrival_dist_type == "Normal":
        arrival_mean = (
            st.number_input(
                "Enter the arrival rate",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        arrival_variance = (
            st.number_input(
                "Enter the arrival variance",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        dist_info.arrival_dist_type = const.NORMAL_DIST
        dist_info.arrival_mean = arrival_mean
        dist_info.arrival_variance = arrival_variance
    elif arrival_dist_type == "Uniform":
        arrival_low = (
            st.number_input(
                "Enter the arrival dist lower limit",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        arrival_high = (
            st.number_input(
                "Enter the arrival dist upper limit",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        dist_info.arrival_dist_type = const.UNIFORM_DIST
        dist_info.arrival_mean = (arrival_low + arrival_high) / 2
        dist_info.arrival_variance = ((arrival_high - arrival_low) ** 2) / 12
        dist_info.arrival_low = arrival_low
        dist_info.arrival_high = arrival_high

    elif arrival_dist_type == "Gamma":
        arrival_shape = (
            st.number_input(
                "Enter the arrival dist shape",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        arrival_scale = (
            st.number_input(
                "Enter the arrival dist scale",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )

        dist_info.arrival_dist_type = const.GAMMA_DIST
        dist_info.arrival_mean = arrival_shape * arrival_scale
        dist_info.arrival_shape = arrival_shape
        dist_info.arrival_scale = arrival_scale

    else:
        arrival_mean = (
            st.number_input(
                "Enter the arrival rate",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        dist_info.arrival_mean = arrival_mean
        dist_info.arrival_dist_type = const.EXP_POIS_RAND_DIST

    # service_mean = st.number_input(
    #     "Enter the service mean", disabled=st.session_state.clicked, min_value=0.001
    # )
    # dist_info.service_mean = service_mean
    if service_dist_type == "Normal":
        service_mean = (
            st.number_input(
                "Enter the service rate",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        service_variance = (
            st.number_input(
                "Enter the service variance",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        dist_info.service_mean = service_mean
        dist_info.service_dist_type = const.NORMAL_DIST
        dist_info.service_variance = service_variance

    elif service_dist_type == "Uniform":
        service_low = (
            st.number_input(
                "Enter the service dist lower limit",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        service_high = (
            st.number_input(
                "Enter the service dist upper limit",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )

        dist_info.service_dist_type = const.UNIFORM_DIST
        dist_info.service_mean = (service_low + service_high) / 2
        dist_info.service_variance = ((service_high - service_low) ** 2) / 12
        dist_info.service_low = service_low
        dist_info.service_high = service_high

    elif service_dist_type == "Gamma":
        service_shape = (
            st.number_input(
                "Enter the service dist shape",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        service_scale = (
            st.number_input(
                "Enter the service dist scale",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )

        dist_info.service_dist_type = const.GAMMA_DIST
        dist_info.service_mean = service_shape * service_scale
        dist_info.service_shape = service_shape
        dist_info.service_scale = service_scale

    else:
        service_mean = (
            st.number_input(
                "Enter the service rate",
                disabled=st.session_state.clicked,
                min_value=0.001,
            )
            * time_factor
        )
        dist_info.service_mean = service_mean
        dist_info.service_dist_type = const.EXP_POIS_RAND_DIST

    st.columns(5)[2].form_submit_button(
        "simulate", on_click=handle_submit, disabled=st.session_state.clicked
    )

if st.session_state.clicked:
    sim = Simulator(num_of_servers, dist_info, is_priority)
    sim.run()

    for _ in range(4):
        st.text("")

    # with st.spinner("Simulating..."):
    #     time.sleep(1.5)

    # st.write(display_table(sim.get_arrival_table()))

    # for _ in range(2):
    #     st.text("")

    st.write(display_table(sim.get_simulation_table()))

    for _ in range(2):
        st.text("")

    for server_index, server in enumerate(sim.servers):
        st.plotly_chart(display_gantt_chart(server_index + 1, server.gantt_chart_data))

    df = sim.df_simulation_table
    # fig, ax = plt.subplots()
    # df.plot.bar(x="id", y="service_time", ax=ax)
    # ax.set_title("Service time for each customer")
    # ax.set_xlabel("Customer ID")
    # ax.set_ylabel("Service Time")
    # st.pyplot(fig)
    if is_priority:
        df.priority = df.priority.apply(str)
    st.bar_chart(
        df, x="id", y="service_time", color="priority" if is_priority else None
    )

    # fig, ax = plt.subplots()
    # df.plot.line(x="id", y="arrival_time", ax=ax)
    # ax.set_title("Arrival time for each customer")
    # ax.set_xlabel("Customer ID")
    # ax.set_ylabel("Arrival Time")
    # st.pyplot(fig)
    # if is_priority:
    #     df.priority = df.priority.apply(str)
    st.bar_chart(
        df, x="id", y="arrival_time", color="priority" if is_priority else None
    )

    # fig, ax = plt.subplots()
    # df.plot.bar(x="id", y="turn_around_time", ax=ax)
    # ax.set_title("Turn Around time for each customer")
    # ax.set_xlabel("Customer ID")
    # ax.set_ylabel("Turn Around Time")
    # st.pyplot(fig)
    # if is_priority:
    #     df.priority = df.priority.apply(str)
    st.bar_chart(
        df, x="id", y="turn_around_time", color="priority" if is_priority else None
    )

    # fig, ax = plt.subplots()
    # df.plot.bar(x="id", y="wait_time", ax=ax)
    # ax.set_title("Waiting time for each customer")
    # ax.set_xlabel("Customer ID")
    # ax.set_ylabel("Waiting Time")
    # st.pyplot(fig)
    # if is_priority:
    #     df.priority = df.priority.apply(str)
    st.bar_chart(df, x="id", y="wait_time", color="priority" if is_priority else None)

    # fig, ax = plt.subplots()
    # df.plot.bar(x="id", y="response_time", ax=ax)
    # ax.set_title("Response time for each customer")
    # ax.set_xlabel("Customer ID")
    # ax.set_ylabel("Response Time")
    # st.pyplot(fig)
    # if is_priority:
    #     df.priority = df.priority.apply(str)
    st.bar_chart(
        df, x="id", y="response_time", color="priority" if is_priority else None
    )

    chart_html = "<html><body>" + css
    for server_index, server in enumerate(sim.servers):
        chart_html += f'<div class="server_head"><h3 style="color: white;">Server {server_index+1}:</h3></div>'
        chart_html += f'<div class="gantt-chart-container">'
        for task in server.gantt_chart_data:
            a = f"""
            <div class="gantt-chart-task" style="background-color: {task["color"]};">
                <div class="gantt-chart-task-label">ID: {task["id"]}</div>
                <div class="gantt-chart-task-timestamp">
                    <span class="start-time" >{task["start"]}</span>
                    <span class="end-time">{task["end"]}</span>
                </div>
            </div>
            """
            # st.write(a, unsafe_allow_html=True)
            chart_html += a
        chart_html += "</div>"
    chart_html += "</body></html>"

    # st.write(chart_html, unsafe_allow_html=True)
    components.html(chart_html, height=300 * len(sim.servers))
    # Reset chart_html for the next iteration
    # chart_html = css

    with st.expander("Show performance measures"):
        averages_points = ""
        for index, item in enumerate(sim.calculate_averages()):
            if index < 4:
                averages_points += f"* {item['name']} = {round(item['value'],3)} mins\n"
            else:
                averages_points += f"* {item['name']} = {round(item['value'],3)}\n"
        st.markdown(averages_points)

    # df = pd.read_csv("prev_averages.csv")
    # avgs = sim.calculate_averages()
    # headers= [avg["name"] for avg in avgs]
    # data = [avg["value"] for avg in avgs]

    # # .to_csv("prev_averages.csv", index=False)
    # df = pd.DataFrame(data, columns=headers)
    # df.to_csv("prev_averages.csv", index=False)

    if method == "FCFS":
        try:
            with st.expander("Show averages using calculations"):
                averages_points = ""
                for item in calculate_averages_by_formula(num_of_servers, dist_info):
                    averages_points += f"* {item['name']} = {round(item['value'],3)}\n"
                st.markdown(averages_points)
        except:
            pass

    st.columns(5)[2].button("Clear", on_click=handle_clear)

    
# os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Set working directory
# subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])