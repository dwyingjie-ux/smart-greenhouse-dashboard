# =====================================================
# COMPACT FULL-WIDTH HISTORICAL TABLE
# =====================================================

st.markdown(
    """
    <style>

    .history-table-container {
        width: 100%;
        overflow-x: hidden;
    }

    .history-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 10px;
    }

    .history-table th {
        border: 1px solid #dddddd;
        padding: 5px 3px;
        text-align: center;
        font-size: 9px;
        font-weight: 600;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.1;
    }

    .history-table td {
        border: 1px solid #dddddd;
        padding: 4px 2px;
        text-align: center;
        font-size: 9px;
        white-space: normal;
        word-wrap: break-word;
        line-height: 1.1;
    }

    .history-table tbody tr:nth-child(even) {
        background-color: rgba(128,128,128,0.04);
    }

    /* Give timestamp slightly more room */
    .history-table th:first-child,
    .history-table td:first-child {
        width: 10%;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {

        .history-table {
            font-size: 6px;
        }

        .history-table th {
            font-size: 5.5px;
            padding: 3px 1px;
        }

        .history-table td {
            font-size: 5.5px;
            padding: 3px 1px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


table_html = table_df.to_html(
    index=False,
    classes="history-table",
    border=0,
    escape=True
)


st.markdown(
    '<div class="history-table-container">'
    + table_html
    + '</div>',
    unsafe_allow_html=True
)
