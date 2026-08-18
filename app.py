import json
import html
import time
import math

import altair as alt
import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Smart Aquaponic Greenhouse",
    page_icon="🌱",
    layout="wide"
)


# =========================================================
# LOGIN DETAILS
# =========================================================

LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin"


# =========================================================
# LOGIN SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================================================
# LOGIN PAGE
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <style>

        .block-container {
            max-width: 500px;
            padding-top: 5rem;
        }

        .login-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .login-subtitle {
            text-align: center;
            color: #777;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="login-title">
            🌱 Smart Aquaponic Greenhouse
        </div>

        <div class="login-subtitle">
            Please login to access the monitoring dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container(border=True):

        with st.form("login_form"):

            username = st.text_input(
                "Username"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_button:

            if (
                username == LOGIN_USERNAME
                and
                password == LOGIN_PASSWORD
            ):

                st.session_state.logged_in = True
                st.rerun()

            else:

                st.error(
                    "Incorrect username or password."
                )

    st.stop()


# =========================================================
# DASHBOARD CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN PAGE
       ===================================================== */

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }


    /* =====================================================
       PAGE TITLE
       ===================================================== */

    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .sub-title {
        font-size: 0.85rem;
        color: #777;
        margin-top: 0.2rem;
        margin-bottom: 0.4rem;
    }

    .last-record {
        font-size: 0.78rem;
        color: #777;
        margin-top: 0.2rem;
    }


    /* =====================================================
       SECTION TITLE
       ===================================================== */

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }


    /* =====================================================
       DASHBOARD GRIDS
       ===================================================== */

    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        width: 100%;
        margin-bottom: 10px;
    }

    .dashboard-grid-3 {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        width: 100%;
        margin-bottom: 10px;
    }

    .dashboard-grid-2 {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        width: 100%;
        margin-bottom: 10px;
    }


    /* =====================================================
       METRIC CARDS
       ===================================================== */

    .metric-card {
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 10px;
        padding: 14px;
        min-height: 105px;
        background: rgba(128, 128, 128, 0.035);

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        text-align: center;
    }

    .metric-label {
        width: 100%;
        font-size: 0.78rem;
        color: #666;
        margin-bottom: 6px;
        text-align: center;
    }

    .metric-value {
        width: 100%;
        font-size: 1.55rem;
        font-weight: 600;
        text-align: center;
    }


    /* =====================================================
       SENSOR STATUS
       ===================================================== */

    .metric-status {
        display: inline-block;
        margin-top: 8px;
        padding: 3px 9px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        text-align: center;
    }


    /* NORMAL */

    .sensor-normal {
        background-color: rgba(46, 160, 67, 0.14);
        color: #16803a;
        border: 1px solid rgba(46, 160, 67, 0.28);
    }


    /* LOW */

    .sensor-low {
        background-color: rgba(245, 158, 11, 0.16);
        color: #b45309;
        border: 1px solid rgba(245, 158, 11, 0.32);
    }


    /* HIGH */

    .sensor-high {
        background-color: rgba(220, 53, 69, 0.14);
        color: #b4232d;
        border: 1px solid rgba(220, 53, 69, 0.28);
    }


    /* UNKNOWN */

    .sensor-unknown {
        background-color: rgba(128, 128, 128, 0.10);
        color: #666;
        border: 1px solid rgba(128, 128, 128, 0.20);
    }


    /* =====================================================
       CONNECTION STATUS
       ===================================================== */

    .status-card {
        border-radius: 9px;
        padding: 12px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        text-align: center;
    }

    .status-online {
        background-color: rgba(46, 160, 67, 0.12);
        color: #16803a;
        border: 1px solid rgba(46, 160, 67, 0.18);
    }

    .status-offline {
        background-color: rgba(220, 53, 69, 0.12);
        color: #b4232d;
        border: 1px solid rgba(220, 53, 69, 0.18);
    }


    /* =====================================================
       LIVE BADGE
       ===================================================== */

    .live-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 20px;
        padding: 4px 10px;
        background-color: rgba(46, 160, 67, 0.12);
        color: #16803a;
        border: 1px solid rgba(46, 160, 67, 0.18);
    }


    /* =====================================================
       COUNTDOWN
       ===================================================== */

    .countdown-box {
        text-align: right;
        font-size: 0.78rem;
        color: #777;
        margin-top: 3px;
        margin-bottom: 4px;
    }

    .countdown-value {
        font-weight: 700;
        color: #16803a;
    }


    /* =====================================================
       CHART
       ===================================================== */

    .chart-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
    }


    /* =====================================================
       STREAMLIT DATAFRAME
       ===================================================== */

    div[data-testid="stDataFrame"] {
        text-align: center;
    }


    /* =====================================================
       PHONE
       ===================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-bottom: 1.2rem;
        }

        .main-title {
            font-size: 1.45rem;
        }

        .sub-title {
            font-size: 0.67rem;
        }

        .last-record {
            font-size: 0.64rem;
        }

        .section-title {
            font-size: 1rem;
        }

        .dashboard-grid,
        .dashboard-grid-3,
        .dashboard-grid-2 {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 7px;
        }

        .metric-card {
            min-height: 82px;
            padding: 9px;
        }

        .metric-label {
            font-size: 0.60rem;
        }

        .metric-value {
            font-size: 1.08rem;
        }

        .metric-status {
            font-size: 0.55rem;
        }

        .status-card {
            padding: 9px 10px;
            font-size: 0.66rem;
        }

        .live-badge {
            font-size: 0.58rem;
        }

        .countdown-box {
            font-size: 0.62rem;
        }

        .chart-title {
            font-size: 0.72rem;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# REFRESH SETTINGS
# =========================================================

REFRESH_SECONDS = 30


# =========================================================
# SENSOR THRESHOLDS
# =========================================================

SENSOR_THRESHOLDS = {

    "fish_tank_level": {
        "low": 30,
        "high": 75
    },

    "fish_temperature": {
        "low": 23,
        "high": 28
    },

    "ph": {
        "low": 6.5,
        "high": 7.5
    },

    "greenhouse_temperature": {
        "low": 25,
        "high": 35
    },

    "soil_moisture": {
        "low": 30,
        "high": 70
    },

    "water_tank_1_level": {
        "low": 20,
        "high": 80
    },

    "water_tank_2_level": {
        "low": 20,
        "high": 80
    }

}


# =========================================================
# AZURE STORAGE SETTINGS
# =========================================================

STORAGE_ACCOUNT_NAME = st.secrets[
    "STORAGE_ACCOUNT_NAME"
]

CONTAINER_NAME = st.secrets[
    "CONTAINER_NAME"
]

STORAGE_ACCOUNT_KEY = st.secrets[
    "STORAGE_ACCOUNT_KEY"
]


ACCOUNT_URL = (
    "https://"
    + STORAGE_ACCOUNT_NAME
    + ".blob.core.windows.net"
)


# =========================================================
# CONNECT TO AZURE
# =========================================================

def get_container_client():

    blob_service_client = BlobServiceClient(
        account_url=ACCOUNT_URL,
        credential=STORAGE_ACCOUNT_KEY
    )

    return blob_service_client.get_container_client(
        CONTAINER_NAME
    )


# =========================================================
# READ BLOB RECORDS
# =========================================================

def read_blob_records(blobs):

    container_client = get_container_client()

    records = []


    for blob in blobs:

        try:

            blob_client = (
                container_client.get_blob_client(
                    blob.name
                )
            )


            raw_data = (
                blob_client
                .download_blob()
                .readall()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
            )


            for line in raw_data.splitlines():

                line = line.strip()


                if not line:
                    continue


                try:

                    records.append(
                        json.loads(
                            line
                        )
                    )

                except json.JSONDecodeError:

                    pass


        except Exception:

            pass


    return records


# =========================================================
# PREPARE DATAFRAME
# =========================================================

def prepare_dataframe(records):

    if len(records) == 0:

        return pd.DataFrame()


    df = pd.DataFrame(
        records
    )


    # =====================================================
    # WATER TANK FIELD COMPATIBILITY
    # =====================================================

    if (
        "water_tank_1" in df.columns
        and
        "water_tank_1_level"
        not in df.columns
    ):

        df[
            "water_tank_1_level"
        ] = df[
            "water_tank_1"
        ]


    if (
        "water_tank_2" in df.columns
        and
        "water_tank_2_level"
        not in df.columns
    ):

        df[
            "water_tank_2_level"
        ] = df[
            "water_tank_2"
        ]


    # =====================================================
    # AZURE HISTORICAL FIELD
    # =====================================================

    if "azure" not in df.columns:

        df[
            "azure"
        ] = "N/A"


    # =====================================================
    # TIMESTAMP
    # =====================================================

    if "timestamp" in df.columns:

        df[
            "timestamp"
        ] = pd.to_datetime(
            df[
                "timestamp"
            ],
            errors="coerce"
        )


        df = df.dropna(
            subset=[
                "timestamp"
            ]
        )


        df = df.drop_duplicates(
            subset=[
                "timestamp"
            ],
            keep="last"
        )


        df = df.sort_values(
            "timestamp"
        )


    return df


# =========================================================
# LOAD RECENT DATA
# =========================================================

def load_recent_data():

    container_client = get_container_client()


    blobs = list(
        container_client.list_blobs()
    )


    if len(blobs) == 0:

        return pd.DataFrame()


    blobs.sort(
        key=lambda blob:
            blob.last_modified,
        reverse=True
    )


    recent_blobs = blobs[:20]


    records = read_blob_records(
        recent_blobs
    )


    return prepare_dataframe(
        records
    )


# =========================================================
# LOAD ALL HISTORICAL DATA
# =========================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def load_all_data():

    container_client = get_container_client()


    blobs = list(
        container_client.list_blobs()
    )


    if len(blobs) == 0:

        return pd.DataFrame()


    blobs.sort(
        key=lambda blob:
            blob.last_modified
    )


    records = read_blob_records(
        blobs
    )


    return prepare_dataframe(
        records
    )


# =========================================================
# DISPLAY VALUE
# =========================================================

def display_value(
    value,
    suffix=""
):

    if value is None:

        return "N/A"


    try:

        if pd.isna(value):

            return "N/A"

    except Exception:

        pass


    return (
        str(value)
        + suffix
    )


# =========================================================
# STATUS VALUE
# =========================================================

def status_value(value):

    if value is None:

        return "UNKNOWN"


    try:

        if pd.isna(value):

            return "UNKNOWN"

    except Exception:

        pass


    return str(
        value
    ).upper()


# =========================================================
# SAFE HTML
# =========================================================

def safe_text(value):

    return html.escape(
        str(value)
    )


# =========================================================
# SENSOR STATUS
# =========================================================

def sensor_status(
    value,
    sensor_name
):

    try:

        value = float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return "UNKNOWN"


    limits = SENSOR_THRESHOLDS.get(
        sensor_name
    )


    if limits is None:

        return "UNKNOWN"


    if value < limits["low"]:

        return "LOW"


    if sensor_name in [
        "fish_tank_level",
        "greenhouse_temperature"
    ]:

        if value >= limits["high"]:

            return "HIGH"


    elif value > limits["high"]:

        return "HIGH"


    return "NORMAL"


# =========================================================
# SENSOR STATUS CLASS
# =========================================================

def sensor_status_class(status):

    status = status_value(
        status
    )


    if status == "NORMAL":

        return "sensor-normal"


    if status == "LOW":

        return "sensor-low"


    if status == "HIGH":

        return "sensor-high"


    return "sensor-unknown"


# =========================================================
# METRIC CARD
# =========================================================

def metric_card(
    label,
    value,
    status=None
):

    status_html = ""


    if status is not None:

        status_text = status_value(
            status
        )


        status_class = sensor_status_class(
            status_text
        )


        status_html = (
            '<div class="metric-status '
            + status_class
            + '">'
            + safe_text(
                "Status: "
                + status_text
            )
            + '</div>'
        )


    return (
        '<div class="metric-card">'
        '<div class="metric-label">'
        + safe_text(label)
        + '</div>'
        '<div class="metric-value">'
        + safe_text(value)
        + '</div>'
        + status_html
        + '</div>'
    )


# =========================================================
# METRIC GRID
# =========================================================

def metric_grid(
    cards,
    columns=4
):

    if columns == 2:

        grid_class = (
            "dashboard-grid-2"
        )

    elif columns == 3:

        grid_class = (
            "dashboard-grid-3"
        )

    else:

        grid_class = (
            "dashboard-grid"
        )


    html_code = (
        '<div class="'
        + grid_class
        + '">'
        + "".join(cards)
        + "</div>"
    )


    st.markdown(
        html_code,
        unsafe_allow_html=True
    )


# =========================================================
# SENSOR CHART
# =========================================================

def sensor_chart(
    df,
    sensor_name,
    title,
    unit=""
):

    if (
        "timestamp" not in df.columns
        or
        sensor_name not in df.columns
    ):

        return


    limits = SENSOR_THRESHOLDS.get(
        sensor_name
    )


    if limits is None:

        return


    chart_df = df[
        [
            "timestamp",
            sensor_name
        ]
    ].copy()


    chart_df[
        sensor_name
    ] = pd.to_numeric(
        chart_df[
            sensor_name
        ],
        errors="coerce"
    )


    chart_df = chart_df.dropna()


    if chart_df.empty:

        return


    st.markdown(
        '<div class="chart-title">'
        + safe_text(
            title
        )
        + '</div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # SENSOR READING
    # =====================================================

    reading_chart = (
        alt.Chart(
            chart_df
        )
        .mark_line(
            strokeWidth=3
        )
        .encode(

            x=alt.X(
                "timestamp:T",
                title="Time"
            ),

            y=alt.Y(
                sensor_name
                + ":Q",
                title=title
                + unit,
                scale=alt.Scale(
                    zero=False
                )
            ),

            color=alt.value(
                "#2563eb"
            ),

            tooltip=[

                alt.Tooltip(
                    "timestamp:T",
                    title="Time",
                    format="%d/%m/%Y %H:%M:%S"
                ),

                alt.Tooltip(
                    sensor_name
                    + ":Q",
                    title=title
                )

            ]

        )
    )


    # =====================================================
    # LOW THRESHOLD
    # =====================================================

    low_df = pd.DataFrame(
        {
            "threshold": [
                limits["low"]
            ]
        }
    )


    low_line = (
        alt.Chart(
            low_df
        )
        .mark_rule(
            strokeWidth=2,
            strokeDash=[
                7,
                5
            ]
        )
        .encode(

            y="threshold:Q",

            color=alt.value(
                "#f59e0b"
            )

        )
    )


    # =====================================================
    # HIGH THRESHOLD
    # =====================================================

    high_df = pd.DataFrame(
        {
            "threshold": [
                limits["high"]
            ]
        }
    )


    high_line = (
        alt.Chart(
            high_df
        )
        .mark_rule(
            strokeWidth=2,
            strokeDash=[
                7,
                5
            ]
        )
        .encode(

            y="threshold:Q",

            color=alt.value(
                "#dc2626"
            )

        )
    )


    # =====================================================
    # LOW LABEL
    # =====================================================

    low_label_df = pd.DataFrame(
        {
            "threshold": [
                limits["low"]
            ],

            "label": [
                "LOW: "
                + str(
                    limits["low"]
                )
                + unit
            ]
        }
    )


    low_label = (
        alt.Chart(
            low_label_df
        )
        .mark_text(
            align="left",
            dx=5,
            dy=-7,
            fontSize=11
        )
        .encode(

            y="threshold:Q",

            text="label:N",

            color=alt.value(
                "#b45309"
            )

        )
    )


    # =====================================================
    # HIGH LABEL
    # =====================================================

    high_label_df = pd.DataFrame(
        {
            "threshold": [
                limits["high"]
            ],

            "label": [
                "HIGH: "
                + str(
                    limits["high"]
                )
                + unit
            ]
        }
    )


    high_label = (
        alt.Chart(
            high_label_df
        )
        .mark_text(
            align="left",
            dx=5,
            dy=-7,
            fontSize=11
        )
        .encode(

            y="threshold:Q",

            text="label:N",

            color=alt.value(
                "#b4232d"
            )

        )
    )


    final_chart = (
        reading_chart
        + low_line
        + high_line
        + low_label
        + high_label
    ).properties(
        height=270
    )


    st.altair_chart(
        final_chart,
        use_container_width=True
    )


# =========================================================
# SIDEBAR
# =========================================================

page = st.sidebar.radio(
    "Menu",
    [
        "Live Dashboard",
        "Historical Data"
    ]
)


st.sidebar.divider()


if st.sidebar.button(
    "Logout",
    use_container_width=True
):

    st.session_state.logged_in = False

    st.rerun()


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '🌱 Smart Aquaponic Greenhouse'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="sub-title">'
    'Azure IoT Monitoring Dashboard'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# LIVE DASHBOARD
# =========================================================

if page == "Live Dashboard":


    # =====================================================
    # SESSION STATE FOR LIVE DATA
    #
    # Streamlit checks every second.
    # Azure is only read every 30 seconds.
    # =====================================================

    if "live_df" not in st.session_state:

        st.session_state.live_df = None


    if "next_dashboard_refresh" not in st.session_state:

        st.session_state.next_dashboard_refresh = 0


    # =====================================================
    # LIVE FRAGMENT
    # =====================================================

    @st.fragment(
        run_every="1s"
    )
    def live_dashboard():


        now = time.time()


        # =================================================
        # READ AZURE ONLY WHEN REQUIRED
        # =================================================

        if (
            st.session_state.live_df is None
            or
            now
            >= st.session_state.next_dashboard_refresh
        ):

            try:

                new_df = load_recent_data()


                if not new_df.empty:

                    st.session_state.live_df = (
                        new_df
                    )


                st.session_state[
                    "next_dashboard_refresh"
                ] = (
                    time.time()
                    + REFRESH_SECONDS
                )


            except Exception as e:

                st.error(
                    "Unable to connect to Azure Blob Storage."
                )

                st.code(
                    str(e)
                )

                return


        # =================================================
        # COUNTDOWN
        # =================================================

        seconds_left = math.ceil(
            st.session_state[
                "next_dashboard_refresh"
            ]
            - time.time()
        )


        seconds_left = max(
            0,
            seconds_left
        )


        st.markdown(
            '<div class="countdown-box">'
            'Next update in: '
            '<span class="countdown-value">'
            + str(seconds_left)
            + 's'
            '</span>'
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # GET STORED LIVE DATA
        # =================================================

        df = st.session_state.live_df


        if (
            df is None
            or
            df.empty
        ):

            st.warning(
                "No greenhouse data found in Azure Blob Storage."
            )

            return


        latest = df.iloc[-1]


        # =================================================
        # LAST SENSOR RECORD
        # =================================================

        record_text = "Unknown"


        if "timestamp" in df.columns:

            latest_time = latest[
                "timestamp"
            ]


            if pd.notna(
                latest_time
            ):

                record_text = (
                    latest_time.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                )


        status_left, status_right = st.columns(
            [
                4,
                1
            ]
        )


        with status_left:

            st.markdown(
                '<div class="last-record">'
                'Last Sensor Record: '
                + safe_text(
                    record_text
                )
                + '</div>',
                unsafe_allow_html=True
            )


        with status_right:

            st.markdown(
                '<div style="text-align:right;">'
                '<span class="live-badge">'
                '● LIVE'
                '</span>'
                '</div>',
                unsafe_allow_html=True
            )


        # =================================================
        # SENSOR STATUS
        # =================================================

        fish_level_status = sensor_status(
            latest.get(
                "fish_tank_level"
            ),
            "fish_tank_level"
        )


        fish_temperature_status = sensor_status(
            latest.get(
                "fish_temperature"
            ),
            "fish_temperature"
        )


        ph_status = sensor_status(
            latest.get(
                "ph"
            ),
            "ph"
        )


        greenhouse_temperature_status = sensor_status(
            latest.get(
                "greenhouse_temperature"
            ),
            "greenhouse_temperature"
        )


        soil_moisture_status = sensor_status(
            latest.get(
                "soil_moisture"
            ),
            "soil_moisture"
        )


        tank1_status = sensor_status(
            latest.get(
                "water_tank_1_level"
            ),
            "water_tank_1_level"
        )


        tank2_status = sensor_status(
            latest.get(
                "water_tank_2_level"
            ),
            "water_tank_2_level"
        )


        # =================================================
        # AQUAPONICS
        # =================================================

        st.divider()


        st.markdown(
            '<div class="section-title">'
            'Aquaponics'
            '</div>',
            unsafe_allow_html=True
        )


        aquaponics_cards = [

            metric_card(
                "Fish Tank Level",

                display_value(
                    latest.get(
                        "fish_tank_level"
                    ),
                    "%"
                ),

                fish_level_status
            ),


            metric_card(
                "Fish Temperature",

                display_value(
                    latest.get(
                        "fish_temperature"
                    ),
                    " °C"
                ),

                fish_temperature_status
            ),


            metric_card(
                "pH",

                display_value(
                    latest.get(
                        "ph"
                    )
                ),

                ph_status
            ),


            metric_card(
                "Fish Refill Pump",

                status_value(
                    latest.get(
                        "fish_refill_pump"
                    )
                )
            )

        ]


        metric_grid(
            aquaponics_cards,
            4
        )


        # =================================================
        # GREENHOUSE
        # =================================================

        st.divider()


        st.markdown(
            '<div class="section-title">'
            'Greenhouse'
            '</div>',
            unsafe_allow_html=True
        )


        greenhouse_cards = [

            metric_card(
                "Temperature",

                display_value(
                    latest.get(
                        "greenhouse_temperature"
                    ),
                    " °C"
                ),

                greenhouse_temperature_status
            ),


            metric_card(
                "Soil Moisture",

                display_value(
                    latest.get(
                        "soil_moisture"
                    ),
                    "%"
                ),

                soil_moisture_status
            ),


            metric_card(
                "Greenhouse Pump",

                status_value(
                    latest.get(
                        "greenhouse_pump"
                    )
                )
            ),


            metric_card(
                "Fan",

                status_value(
                    latest.get(
                        "fan"
                    )
                )
            )

        ]


        metric_grid(
            greenhouse_cards,
            4
        )


        # =================================================
        # WATER SYSTEM
        # =================================================

        st.divider()


        st.markdown(
            '<div class="section-title">'
            'Water System'
            '</div>',
            unsafe_allow_html=True
        )


        water_cards = [

            metric_card(
                "Water Tank 1",

                display_value(
                    latest.get(
                        "water_tank_1_level"
                    ),
                    "%"
                ),

                tank1_status
            ),


            metric_card(
                "Water Tank 2",

                display_value(
                    latest.get(
                        "water_tank_2_level"
                    ),
                    "%"
                ),

                tank2_status
            )

        ]


        metric_grid(
            water_cards,
            2
        )


        # =================================================
        # CONNECTION
        # =================================================

        st.divider()


        st.markdown(
            '<div class="section-title">'
            'Connection'
            '</div>',
            unsafe_allow_html=True
        )


        wifi_status = status_value(
            latest.get(
                "wifi"
            )
        )


        if wifi_status == "ONLINE":

            wifi_class = (
                "status-card status-online"
            )

        else:

            wifi_class = (
                "status-card status-offline"
            )


        connection_html = (

            '<div class="dashboard-grid-2">'


            '<div class="'
            + wifi_class
            + '">'
            'Wi-Fi: '
            + safe_text(
                wifi_status
            )
            + '</div>'


            '<div class="status-card status-online">'
            'Azure: ONLINE'
            '</div>'


            '</div>'
        )


        st.markdown(
            connection_html,
            unsafe_allow_html=True
        )


        # =================================================
        # SENSOR HISTORY
        # =================================================

        st.divider()


        st.markdown(
            '<div class="section-title">'
            'Sensor History'
            '</div>',
            unsafe_allow_html=True
        )


        st.caption(
            "Blue = Sensor Reading  |  "
            "Yellow = LOW Threshold  |  "
            "Red = HIGH Threshold"
        )


        # =================================================
        # ROW 1
        # =================================================

        chart1, chart2 = st.columns(
            2
        )


        with chart1:

            sensor_chart(
                df,
                "fish_tank_level",
                "Fish Tank Level",
                "%"
            )


        with chart2:

            sensor_chart(
                df,
                "fish_temperature",
                "Fish Temperature",
                " °C"
            )


        # =================================================
        # ROW 2
        # =================================================

        chart1, chart2 = st.columns(
            2
        )


        with chart1:

            sensor_chart(
                df,
                "ph",
                "pH Level"
            )


        with chart2:

            sensor_chart(
                df,
                "greenhouse_temperature",
                "Greenhouse Temperature",
                " °C"
            )


        # =================================================
        # ROW 3
        # =================================================

        chart1, chart2 = st.columns(
            2
        )


        with chart1:

            sensor_chart(
                df,
                "soil_moisture",
                "Soil Moisture",
                "%"
            )


        with chart2:

            sensor_chart(
                df,
                "water_tank_1_level",
                "Water Tank 1",
                "%"
            )


        # =================================================
        # ROW 4
        # =================================================

        sensor_chart(
            df,
            "water_tank_2_level",
            "Water Tank 2",
            "%"
        )


        # =================================================
        # FOOTER
        # =================================================

        st.caption(
            "Data source: "
            "Azure IoT Hub → "
            "Stream Analytics → "
            "Azure Blob Storage"
        )


    live_dashboard()


# =========================================================
# HISTORICAL DATA
# =========================================================

elif page == "Historical Data":


    st.divider()


    st.markdown(
        '<div class="section-title">'
        'Historical Sensor Data'
        '</div>',
        unsafe_allow_html=True
    )


    st.caption(
        "Important greenhouse, fish, water and connection records."
    )


    # =====================================================
    # REFRESH HISTORICAL DATA
    # =====================================================

    if st.button(
        "Refresh Historical Data"
    ):

        st.cache_data.clear()

        st.rerun()


    # =====================================================
    # LOAD HISTORICAL DATA
    # =====================================================

    try:

        with st.spinner(
            "Loading historical data from Azure..."
        ):

            history_df = load_all_data()


    except Exception as e:

        st.error(
            "Unable to load historical data."
        )

        st.code(
            str(e)
        )

        st.stop()


    if history_df.empty:

        st.warning(
            "No historical records found."
        )

        st.stop()


    # =====================================================
    # SUMMARY
    # =====================================================

    total_records = len(
        history_df
    )


    first_record = (
        history_df[
            "timestamp"
        ].min()
        if
        "timestamp"
        in history_df.columns
        else None
    )


    latest_record = (
        history_df[
            "timestamp"
        ].max()
        if
        "timestamp"
        in history_df.columns
        else None
    )


    col1, col2, col3 = st.columns(
        3
    )


    with col1:

        st.metric(
            "Total Records",
            total_records
        )


    with col2:

        if first_record is not None:

            st.metric(
                "Oldest Record",
                first_record.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )


    with col3:

        if latest_record is not None:

            st.metric(
                "Latest Record",
                latest_record.strftime(
                    "%d/%m/%Y %H:%M"
                )
            )


    # =====================================================
    # DATE FILTER
    # =====================================================

    st.divider()


    filtered_df = history_df.copy()


    if (
        "timestamp"
        in filtered_df.columns
    ):

        minimum_date = (
            filtered_df[
                "timestamp"
            ]
            .min()
            .date()
        )


        maximum_date = (
            filtered_df[
                "timestamp"
            ]
            .max()
            .date()
        )


        selected_dates = st.date_input(
            "Filter by Date",

            value=(
                minimum_date,
                maximum_date
            ),

            min_value=minimum_date,

            max_value=maximum_date
        )


        if (
            isinstance(
                selected_dates,
                tuple
            )
            and
            len(
                selected_dates
            ) == 2
        ):

            start_date = (
                selected_dates[
                    0
                ]
            )


            end_date = (
                selected_dates[
                    1
                ]
            )


            filtered_df = filtered_df[
                (
                    filtered_df[
                        "timestamp"
                    ].dt.date
                    >= start_date
                )
                &
                (
                    filtered_df[
                        "timestamp"
                    ].dt.date
                    <= end_date
                )
            ]


    # =====================================================
    # IMPORTANT HISTORICAL COLUMNS
    #
    # ORDER:
    #
    # GREENHOUSE
    # FISH
    # WATER
    # CONNECTION
    # =====================================================

    preferred_columns = [

        # Time
        "timestamp",

        # Greenhouse
        "greenhouse_temperature",
        "soil_moisture",
        "fan",
        "greenhouse_pump",

        # Fish
        "fish_tank_level",
        "ph",
        "fish_refill_pump",

        # Water
        "water_tank_1_level",
        "water_tank_2_level",

        # Connection
        "wifi",
        "azure"

    ]


    available_columns = [

        column

        for column
        in preferred_columns

        if column
        in filtered_df.columns

    ]


    table_df = (
        filtered_df[
            available_columns
        ]
        .copy()
    )


    # =====================================================
    # SORT NEWEST FIRST
    # =====================================================

    if (
        "timestamp"
        in table_df.columns
    ):

        table_df = table_df.sort_values(
            "timestamp",
            ascending=False
        )


        table_df[
            "timestamp"
        ] = (
            table_df[
                "timestamp"
            ]
            .dt.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )


    # =====================================================
    # SHORT COLUMN NAMES
    # =====================================================

    table_df = table_df.rename(
        columns={

            "timestamp":
                "Timestamp",

            "greenhouse_temperature":
                "GH Temp",

            "soil_moisture":
                "Soil",

            "fan":
                "Fan",

            "greenhouse_pump":
                "GH Pump",

            "fish_tank_level":
                "Fish Tank",

            "ph":
                "pH",

            "fish_refill_pump":
                "Refill Pump",

            "water_tank_1_level":
                "Tank 1",

            "water_tank_2_level":
                "Tank 2",

            "wifi":
                "Wi-Fi",

            "azure":
                "Azure"

        }
    )


    # =====================================================
    # RECORD COUNT
    # =====================================================

    st.write(
        "Showing",
        len(
            table_df
        ),
        "of",
        total_records,
        "records"
    )


    # =====================================================
    # CENTRE HISTORICAL TABLE
    # =====================================================

    centered_table = (

        table_df.style

        .set_properties(
            **{
                "text-align":
                    "center"
            }
        )

        .set_table_styles(
            [

                {
                    "selector":
                        "th",

                    "props": [
                        (
                            "text-align",
                            "center"
                        )
                    ]
                },

                {
                    "selector":
                        "td",

                    "props": [
                        (
                            "text-align",
                            "center"
                        )
                    ]
                }

            ]
        )

    )


    st.dataframe(
        centered_table,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # DOWNLOAD CSV
    # =====================================================

    csv_data = (
        table_df
        .to_csv(
            index=False
        )
        .encode(
            "utf-8"
        )
    )


    st.download_button(
        label=(
            "Download Historical Data CSV"
        ),

        data=csv_data,

        file_name=(
            "smart_aquaponic_greenhouse_history.csv"
        ),

        mime="text/csv"
    )


    # =====================================================
    # FOOTER
    # =====================================================

    st.caption(
        "Historical data source: "
        "Azure Blob Storage - "
        + CONTAINER_NAME
    )
