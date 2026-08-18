import json

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
# AZURE STORAGE SETTINGS
# =========================================================

STORAGE_ACCOUNT_NAME = st.secrets["STORAGE_ACCOUNT_NAME"]

CONTAINER_NAME = st.secrets["CONTAINER_NAME"]


# =========================================================
# STORAGE ACCOUNT KEY
#
# Paste your Azure Storage Account Key below.
# =========================================================

STORAGE_ACCOUNT_KEY = st.secrets["STORAGE_ACCOUNT_KEY"]


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
# LOAD DATA FROM AZURE
#
# NO CACHE HERE.
#
# Every live refresh should ask Azure for
# the latest Blob data.
# =========================================================

def load_data():

    container_client = (
        get_container_client()
    )


    # =====================================================
    # LIST ALL BLOBS
    # =====================================================

    blobs = list(
        container_client.list_blobs()
    )


    if len(blobs) == 0:

        return pd.DataFrame()


    # =====================================================
    # NEWEST BLOBS FIRST
    # =====================================================

    blobs.sort(
        key=lambda blob: blob.last_modified,
        reverse=True
    )


    # =====================================================
    # READ RECENT BLOBS
    #
    # Enough for latest readings + charts
    # =====================================================

    recent_blobs = blobs[:20]


    records = []


    # =====================================================
    # READ EACH BLOB
    # =====================================================

    for blob in recent_blobs:

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


            # =================================================
            # ONE JSON RECORD PER LINE
            # =================================================

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


    # =====================================================
    # NO VALID DATA
    # =====================================================

    if len(records) == 0:

        return pd.DataFrame()


    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    df = pd.DataFrame(
        records
    )


    # =====================================================
    # TIMESTAMP
    # =====================================================

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


        # Remove duplicates if same records
        # appear across blobs
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
# DISPLAY VALUE
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

    except:

        pass


    return (
        str(value)
        + suffix
    )


# =========================================================
# STATUS VALUE
# =========================================================

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

    except:

        pass


    return str(
        value
    ).upper()


# =========================================================
# PAGE TITLE
# =========================================================

st.title(
    "🌱 Smart Aquaponic Greenhouse"
)

st.caption(
    "Azure IoT Live Monitoring Dashboard"
)


# =========================================================
# LIVE DASHBOARD
#
# Streamlit automatically reruns this section
# every 10 seconds while the page is open.
# =========================================================

@st.fragment(
    run_every="10s"
)
def live_dashboard():


    # =====================================================
    # LOAD LATEST AZURE DATA
    # =====================================================

    try:

        df = load_data()


    except Exception as e:

        st.error(
            "Unable to connect to Azure Blob Storage."
        )

        st.code(
            str(e)
        )

        return


    # =====================================================
    # CHECK DATA
    # =====================================================

    if df.empty:

        st.warning(
            "No greenhouse data found in Azure Blob Storage."
        )

        return


    # =====================================================
    # LATEST RECORD
    # =====================================================

    latest = df.iloc[-1]


    # =====================================================
    # LIVE REFRESH STATUS
    # =====================================================

    top_left, top_right = st.columns(
        [3, 1]
    )


    with top_left:

        if "timestamp" in df.columns:

            latest_time = latest[
                "timestamp"
            ]


            if pd.notna(
                latest_time
            ):

                st.caption(
                    "Last Updated: "
                    + latest_time.strftime(
                        "%d/%m/%Y %H:%M:%S"
                    )
                )


    with top_right:

        st.success(
            "● LIVE"
        )


    # =====================================================
    # AQUAPONICS
    # =====================================================

    st.divider()

    st.subheader(
        "Aquaponics"
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.metric(
            "Fish Tank Level",
            display_value(
                latest.get(
                    "fish_tank_level"
                ),
                "%"
            )
        )


    with col2:

        st.metric(
            "Fish Temperature",
            display_value(
                latest.get(
                    "fish_temperature"
                ),
                " °C"
            )
        )


    with col3:

        st.metric(
            "pH",
            display_value(
                latest.get(
                    "ph"
                )
            )
        )

        st.caption(
            "Status: "
            + status_value(
                latest.get(
                    "ph_alert"
                )
            )
        )


    with col4:

        st.metric(
            "Fish Refill Pump",
            status_value(
                latest.get(
                    "fish_refill_pump"
                )
            )
        )


    # =====================================================
    # GREENHOUSE
    # =====================================================

    st.divider()

    st.subheader(
        "Greenhouse"
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    with col1:

        st.metric(
            "Temperature",
            display_value(
                latest.get(
                    "greenhouse_temperature"
                ),
                " °C"
            )
        )


    with col2:

        st.metric(
            "Soil Moisture",
            display_value(
                latest.get(
                    "soil_moisture"
                ),
                "%"
            )
        )


    with col3:

        st.metric(
            "Greenhouse Pump",
            status_value(
                latest.get(
                    "greenhouse_pump"
                )
            )
        )


    with col4:

        st.metric(
            "Fan",
            status_value(
                latest.get(
                    "fan"
                )
            )
        )


    # =====================================================
    # WATER SYSTEM
    # =====================================================

    st.divider()

    st.subheader(
        "Water System"
    )


    col1, col2, col3 = st.columns(
        3
    )


    with col1:

        st.metric(
            "Water Tank 1",
            display_value(
                latest.get(
                    "water_tank_1_level"
                ),
                "%"
            )
        )


    with col2:

        st.metric(
            "Water Tank 2",
            display_value(
                latest.get(
                    "water_tank_2_level"
                ),
                "%"
            )
        )


    with col3:

        st.metric(
            "Water Status",
            status_value(
                latest.get(
                    "water_alert"
                )
            )
        )


    # =====================================================
    # CONNECTION
    # =====================================================

    st.divider()

    st.subheader(
        "Connection"
    )


    col1, col2 = st.columns(
        2
    )


    with col1:

        wifi_status = status_value(
            latest.get(
                "wifi"
            )
        )


        if wifi_status == "ONLINE":

            st.success(
                "Wi-Fi: ONLINE"
            )

        else:

            st.error(
                "Wi-Fi: "
                + wifi_status
            )


    with col2:

        # Since this page successfully retrieved
        # data from Azure Blob Storage.
        st.success(
            "Azure: ONLINE"
        )


    # =====================================================
    # SENSOR HISTORY
    # =====================================================

    st.divider()

    st.subheader(
        "Sensor History"
    )


    # =====================================================
    # GREENHOUSE TEMPERATURE
    # =====================================================

    if (
        "timestamp" in df.columns
        and
        "greenhouse_temperature"
        in df.columns
    ):

        st.write(
            "Greenhouse Temperature"
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
            temperature_chart
        )


    # =====================================================
    # PH HISTORY
    # =====================================================

    if (
        "timestamp" in df.columns
        and
        "ph" in df.columns
    ):

        st.write(
            "pH Level"
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
            ph_chart
        )


    # =====================================================
    # SOIL MOISTURE HISTORY
    # =====================================================

    if (
        "timestamp" in df.columns
        and
        "soil_moisture"
        in df.columns
    ):

        st.write(
            "Soil Moisture"
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
            soil_chart
        )


    # =====================================================
    # RAW DATA
    # =====================================================

    st.divider()


    with st.expander(
        "View Azure Raw Data"
    ):

        if "timestamp" in df.columns:

            raw_df = df.sort_values(
                "timestamp",
                ascending=False
            )

        else:

            raw_df = df


        st.dataframe(
            raw_df,
            use_container_width=True
        )


    # =====================================================
    # FOOTER
    # =====================================================

    st.caption(
        "Data source: "
        "Azure IoT Hub → "
        "Stream Analytics → "
        "Azure Blob Storage"
    )

    st.caption(
        "Live dashboard refresh: every 10 seconds"
    )


# =========================================================
# RUN LIVE DASHBOARD
# =========================================================

live_dashboard()
