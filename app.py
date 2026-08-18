import json
import html
from datetime import date

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
# RESPONSIVE CSS
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
        max-width: 1400px;
    }


    /* =====================================================
       TITLE
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
       DASHBOARD GRID
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
        padding: 14px 14px 12px 14px;
        min-height: 92px;
        background: rgba(128, 128, 128, 0.035);
        overflow: hidden;
    }

    .metric-label {
        font-size: 0.78rem;
        color: #666;
        margin-bottom: 6px;
        line-height: 1.15;
    }

    .metric-value {
        font-size: 1.55rem;
        font-weight: 600;
        line-height: 1.15;
        overflow-wrap: anywhere;
    }

    .metric-status {
        font-size: 0.68rem;
        color: #777;
        margin-top: 6px;
        line-height: 1.15;
    }


    /* =====================================================
       CONNECTION STATUS
       ===================================================== */

    .status-card {
        border-radius: 9px;
        padding: 12px 14px;
        font-size: 0.82rem;
        font-weight: 500;
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
       CHART TITLE
       ===================================================== */

    .chart-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
    }


    /* =====================================================
       HISTORY INFORMATION
       ===================================================== */

    .history-info {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
        margin-bottom: 0.5rem;
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
            line-height: 1.2;
        }

        .sub-title {
            font-size: 0.67rem;
        }

        .last-record {
            font-size: 0.64rem;
        }

        .section-title {
            font-size: 1rem;
            margin-top: 0.65rem;
            margin-bottom: 0.45rem;
        }

        .dashboard-grid,
        .dashboard-grid-3,
        .dashboard-grid-2 {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 7px;
        }

        .metric-card {
            min-height: 72px;
            padding: 9px 9px 8px 9px;
            border-radius: 8px;
        }

        .metric-label {
            font-size: 0.60rem;
            margin-bottom: 4px;
        }

        .metric-value {
            font-size: 1.08rem;
        }

        .metric-status {
            font-size: 0.55rem;
            margin-top: 4px;
        }

        .status-card {
            padding: 9px 10px;
            font-size: 0.66rem;
        }

        .live-badge {
            font-size: 0.58rem;
            padding: 3px 7px;
        }

        .chart-title {
            font-size: 0.72rem;
        }

        .history-info {
            font-size: 0.65rem;
        }

        [data-testid="stVegaLiteChart"] {
            width: 100% !important;
        }

        [data-testid="stDataFrame"] {
            font-size: 0.65rem;
        }

        hr {
            margin-top: 0.8rem !important;
            margin-bottom: 0.8rem !important;
        }

        [data-testid="stExpander"] {
            font-size: 0.7rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


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


# =========================================================
# AZURE STORAGE URL
# =========================================================

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
# READ BLOBS
# =========================================================

def read_blob_records(blobs):

    container_client = (
        get_container_client()
    )

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

                    record = json.loads(
                        line
                    )

                    records.append(
                        record
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


    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
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
#
# Used by Live Dashboard
# =========================================================

def load_recent_data():

    container_client = (
        get_container_client()
    )

    blobs = list(
        container_client.list_blobs()
    )


    if len(blobs) == 0:

        return pd.DataFrame()


    blobs.sort(
        key=lambda blob: blob.last_modified,
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
#
# Used only on Historical Data page.
# =========================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def load_all_data():

    container_client = (
        get_container_client()
    )

    blobs = list(
        container_client.list_blobs()
    )


    if len(blobs) == 0:

        return pd.DataFrame()


    blobs.sort(
        key=lambda blob: blob.last_modified
    )


    records = read_blob_records(
        blobs
    )


    return prepare_dataframe(
        records
    )


# =========================================================
# VALUE HELPERS
# =========================================================

def display_value(
    value,
    suffix=""
):

    if value is None:

        return "N/A"


    try:

        if pd.isna(
            value
        ):

            return "N/A"

    except Exception:

        pass


    return (
        str(value)
        + suffix
    )


def status_value(
    value
):

    if value is None:

        return "UNKNOWN"


    try:

        if pd.isna(
            value
        ):

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
# METRIC CARD
# =========================================================

def metric_card(
    label,
    value,
    status=None
):

    status_html = ""


    if status is not None:

        status_html = (
            '<div class="metric-status">'
            + safe_text(status)
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

        grid_class = "dashboard-grid-2"

    elif columns == 3:

        grid_class = "dashboard-grid-3"

    else:

        grid_class = "dashboard-grid"


    html_code = (
        '<div class="'
        + grid_class
        + '">'
    )


    for card in cards:

        html_code += card


    html_code += "</div>"


    st.markdown(
        html_code,
        unsafe_allow_html=True
    )


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🌱 Greenhouse"
)

page = st.sidebar.radio(
    "Menu",
    [
        "Live Dashboard",
        "Historical Data"
    ]
)


# =========================================================
# PAGE TITLE
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
# LIVE DASHBOARD PAGE
# =========================================================

if page == "Live Dashboard":


    # =====================================================
    # LIVE FRAGMENT
    #
    # Refresh every 1 minute
    # =====================================================

    @st.fragment(
        run_every="60s"
    )
    def live_dashboard():


        try:

            df = load_recent_data()


        except Exception as e:

            st.error(
                "Unable to connect to Azure Blob Storage."
            )

            st.code(
                str(e)
            )

            return


        if df.empty:

            st.warning(
                "No greenhouse data found in Azure Blob Storage."
            )

            return


        # =================================================
        # LATEST RECORD
        # =================================================

        latest = df.iloc[-1]


        # =================================================
        # RECORD TIMESTAMP
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
            [4, 1]
        )


        with status_left:

            st.markdown(
                '<div class="last-record">'
                'Last Sensor Record: '
                + safe_text(record_text)
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
        # AQUAPONICS
        # =================================================

        st.divider()

        st.markdown(
            '<div class="section-title">'
            'Aquaponics'
            '</div>',
            unsafe_allow_html=True
        )


        ph_status = status_value(
            latest.get(
                "ph_alert"
            )
        )


        aquaponics_cards = [

            metric_card(
                "Fish Tank Level",
                display_value(
                    latest.get(
                        "fish_tank_level"
                    ),
                    "%"
                )
            ),

            metric_card(
                "Fish Temperature",
                display_value(
                    latest.get(
                        "fish_temperature"
                    ),
                    " °C"
                )
            ),

            metric_card(
                "pH",
                display_value(
                    latest.get(
                        "ph"
                    )
                ),
                "Status: " + ph_status
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
                )
            ),

            metric_card(
                "Soil Moisture",
                display_value(
                    latest.get(
                        "soil_moisture"
                    ),
                    "%"
                )
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
                )
            ),

            metric_card(
                "Water Tank 2",
                display_value(
                    latest.get(
                        "water_tank_2_level"
                    ),
                    "%"
                )
            ),

            metric_card(
                "Water Status",
                status_value(
                    latest.get(
                        "water_alert"
                    )
                )
            )

        ]


        metric_grid(
            water_cards,
            3
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


        # =================================================
        # TEMPERATURE CHART
        # =================================================

        if (
            "timestamp" in df.columns
            and
            "greenhouse_temperature" in df.columns
        ):

            st.markdown(
                '<div class="chart-title">'
                'Greenhouse Temperature'
                '</div>',
                unsafe_allow_html=True
            )


            temperature_chart = (
                df[
                    [
                        "timestamp",
                        "greenhouse_temperature"
                    ]
                ]
                .dropna()
                .set_index(
                    "timestamp"
                )
            )


            st.line_chart(
                temperature_chart,
                use_container_width=True
            )


        # =================================================
        # PH CHART
        # =================================================

        if (
            "timestamp" in df.columns
            and
            "ph" in df.columns
        ):

            st.markdown(
                '<div class="chart-title">'
                'pH Level'
                '</div>',
                unsafe_allow_html=True
            )


            ph_chart = (
                df[
                    [
                        "timestamp",
                        "ph"
                    ]
                ]
                .dropna()
                .set_index(
                    "timestamp"
                )
            )


            st.line_chart(
                ph_chart,
                use_container_width=True
            )


        # =================================================
        # SOIL MOISTURE CHART
        # =================================================

        if (
            "timestamp" in df.columns
            and
            "soil_moisture" in df.columns
        ):

            st.markdown(
                '<div class="chart-title">'
                'Soil Moisture'
                '</div>',
                unsafe_allow_html=True
            )


            soil_chart = (
                df[
                    [
                        "timestamp",
                        "soil_moisture"
                    ]
                ]
                .dropna()
                .set_index(
                    "timestamp"
                )
            )


            st.line_chart(
                soil_chart,
                use_container_width=True
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


    # =====================================================
    # RUN LIVE DASHBOARD
    # =====================================================

    live_dashboard()


# =========================================================
# HISTORICAL DATA PAGE
# =========================================================

elif page == "Historical Data":


    st.divider()

    st.markdown(
        '<div class="section-title">'
        'Historical Sensor Data'
        '</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="history-info">'
        'All available IoT records stored in '
        'Azure Blob Storage.'
        '</div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # MANUAL RELOAD BUTTON
    # =====================================================

    if st.button(
        "Refresh Historical Data"
    ):

        st.cache_data.clear()

        st.rerun()


    # =====================================================
    # LOAD ALL DATA
    # =====================================================

    try:

        with st.spinner(
            "Loading historical data from Azure..."
        ):

            history_df = (
                load_all_data()
            )


    except Exception as e:

        st.error(
            "Unable to load historical data."
        )

        st.code(
            str(e)
        )

        st.stop()


    # =====================================================
    # NO DATA
    # =====================================================

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
        if "timestamp" in history_df.columns
        else None
    )


    latest_record = (
        history_df[
            "timestamp"
        ].max()
        if "timestamp" in history_df.columns
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

    filtered_df = (
        history_df.copy()
    )


    if "timestamp" in filtered_df.columns:

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


        if isinstance(
            selected_dates,
            tuple
        ):

            if len(
                selected_dates
            ) == 2:

                start_date = (
                    selected_dates[0]
                )

                end_date = (
                    selected_dates[1]
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
    # STATUS FILTER
    # =====================================================

    filter_col1, filter_col2 = (
        st.columns(
            2
        )
    )


    with filter_col1:

        if (
            "ph_alert"
            in filtered_df.columns
        ):

            ph_options = (
                sorted(
                    filtered_df[
                        "ph_alert"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                )
            )


            selected_ph = (
                st.multiselect(
                    "pH Status",
                    ph_options
                )
            )


            if selected_ph:

                filtered_df = (
                    filtered_df[
                        filtered_df[
                            "ph_alert"
                        ]
                        .astype(str)
                        .isin(
                            selected_ph
                        )
                    ]
                )


    with filter_col2:

        if (
            "water_alert"
            in filtered_df.columns
        ):

            water_options = (
                sorted(
                    filtered_df[
                        "water_alert"
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                )
            )


            selected_water = (
                st.multiselect(
                    "Water Status",
                    water_options
                )
            )


            if selected_water:

                filtered_df = (
                    filtered_df[
                        filtered_df[
                            "water_alert"
                        ]
                        .astype(str)
                        .isin(
                            selected_water
                        )
                    ]
                )


    # =====================================================
    # SELECT FINAL TABLE COLUMNS
    # =====================================================

    preferred_columns = [

        "timestamp",

        "fish_tank_level",
        "fish_temperature",
        "ph",
        "ph_alert",
        "fish_refill_pump",

        "greenhouse_temperature",
        "soil_moisture",
        "greenhouse_pump",
        "fan",

        "water_tank_1_level",
        "water_tank_2_level",
        "water_alert",

        "dht_status",
        "wifi",

        "device"

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
    # FORMAT TIMESTAMP
    # =====================================================

    if "timestamp" in table_df.columns:

        table_df = (
            table_df.sort_values(
                "timestamp",
                ascending=False
            )
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
    # FRIENDLY COLUMN NAMES
    # =====================================================

    table_df = table_df.rename(
        columns={

            "timestamp":
                "Timestamp",

            "fish_tank_level":
                "Fish Tank Level (%)",

            "fish_temperature":
                "Fish Temp (°C)",

            "ph":
                "pH",

            "ph_alert":
                "pH Status",

            "fish_refill_pump":
                "Fish Refill Pump",

            "greenhouse_temperature":
                "Greenhouse Temp (°C)",

            "soil_moisture":
                "Soil Moisture (%)",

            "greenhouse_pump":
                "Greenhouse Pump",

            "fan":
                "Fan",

            "water_tank_1_level":
                "Water Tank 1 (%)",

            "water_tank_2_level":
                "Water Tank 2 (%)",

            "water_alert":
                "Water Status",

            "dht_status":
                "Temperature Sensor",

            "wifi":
                "Wi-Fi",

            "device":
                "Device"

        }
    )


    # =====================================================
    # DISPLAY RECORD COUNT
    # =====================================================

    st.write(
        "Showing",
        len(table_df),
        "of",
        total_records,
        "records"
    )


    # =====================================================
    # HISTORICAL DATA TABLE
    # =====================================================

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=600
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
        label="Download Historical Data CSV",
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
