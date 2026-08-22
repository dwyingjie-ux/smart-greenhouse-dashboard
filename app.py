def prepare_dataframe(records):

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(
        records
    )

    # =====================================================
    # WATER TANK COLUMN COMPATIBILITY
    # =====================================================

    if (
        "water_tank_1" in df.columns
        and
        "water_tank_1_level" not in df.columns
    ):

        df[
            "water_tank_1_level"
        ] = df[
            "water_tank_1"
        ]

    if (
        "water_tank_2" in df.columns
        and
        "water_tank_2_level" not in df.columns
    ):

        df[
            "water_tank_2_level"
        ] = df[
            "water_tank_2"
        ]

    # =====================================================
    # TIMESTAMP
    #
    # Azure Stream Analytics already adds +8 hours.
    # Therefore the stored timestamp represents
    # Singapore local time.
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

        # Azure timestamp is already Singapore time.
        # Attach Singapore timezone without adding
        # another 8 hours.
        if df["timestamp"].dt.tz is None:

            df["timestamp"] = (
                df["timestamp"]
                .dt.tz_localize(
                    "Asia/Singapore"
                )
            )

        else:

            df["timestamp"] = (
                df["timestamp"]
                .dt.tz_convert(
                    "Asia/Singapore"
                )
            )

        # Remove duplicate timestamps
        df = df.drop_duplicates(
            subset=[
                "timestamp"
            ],
            keep="last"
        )

        # =================================================
        # FUTURE TIMESTAMP PROTECTION
        # =================================================

        now_sg = pd.Timestamp.now(
            tz="Asia/Singapore"
        )

        future_limit = (
            now_sg
            + pd.Timedelta(
                seconds=FUTURE_TIMESTAMP_TOLERANCE_SECONDS
            )
        )

        df = df[
            df["timestamp"] <= future_limit
        ]

        # Oldest → newest
        df = df.sort_values(
            "timestamp"
        )

    return df
