import streamlit as st
import pandas as pd
import plotly.express as px

from analyzer import analyze_excel


# =====================================================
# PAGE SETTINGS
# =====================================================

st.set_page_config(
    page_title="Excel Dashboard",
    page_icon="📊",
    layout="wide"
)


# =====================================================
# TITLE
# =====================================================

st.title("📊 Excel Report Dashboard")

st.write(
    "Upload an Excel file and explore your data interactively."
)


# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "📁 Upload Excel File",
    type=["xlsx", "xls"]
)


if uploaded_file is not None:

    # =================================================
    # READ EXCEL FILE
    # =================================================

    try:

        result = analyze_excel(uploaded_file)

        df = result["data"].copy()

    except Exception as e:

        st.error(
            f"Unable to read the Excel file: {e}"
        )

        st.stop()


    # =================================================
    # SIDEBAR
    # =================================================

    st.sidebar.header("⚙️ Dashboard Controls")

    st.sidebar.success(
        "Excel file loaded successfully!"
    )


    # =================================================
    # RESET FILTERS
    # =================================================

    if st.sidebar.button("🔄 Reset Filters"):

        st.rerun()


    # =================================================
    # FILTERS
    # =================================================

    st.sidebar.subheader("🔎 Filters")

    categorical_columns = df.select_dtypes(
        include=["object", "string", "category"]
    ).columns.tolist()

    filtered_df = df.copy()


    for column in categorical_columns:

        unique_values = (
            df[column]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if 0 < len(unique_values) <= 50:

            selected_values = st.sidebar.multiselect(
                f"Filter {column}",
                options=sorted(unique_values),
                default=sorted(unique_values),
                key=f"filter_{column}"
            )

            if selected_values:

                filtered_df = filtered_df[
                    filtered_df[column]
                    .astype(str)
                    .isin(selected_values)
                ]


    # =================================================
    # DASHBOARD OVERVIEW
    # =================================================

    st.subheader("📌 Dashboard Overview")

    numeric_columns = filtered_df.select_dtypes(
        include="number"
    ).columns.tolist()

    total_rows = len(filtered_df)

    total_columns = len(filtered_df.columns)

    missing_count = int(
        filtered_df.isnull().sum().sum()
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "📄 Total Rows",
            f"{total_rows:,}"
        )


    with col2:

        st.metric(
            "📊 Total Columns",
            f"{total_columns:,}"
        )


    with col3:

        st.metric(
            "🔢 Numeric Columns",
            f"{len(numeric_columns):,}"
        )


    with col4:

        st.metric(
            "⚠️ Missing Values",
            f"{missing_count:,}"
        )


    # =================================================
    # SEARCH DATA
    # =================================================

    st.subheader("📋 Interactive Data")

    search_text = st.text_input(
        "🔎 Search the dataset",
        placeholder="Type something to search..."
    )


    if search_text:

        search_mask = filtered_df.astype(
            str
        ).apply(
            lambda row: row.str.contains(
                search_text,
                case=False,
                na=False
            ).any(),
            axis=1
        )

        filtered_df = filtered_df[
            search_mask
        ]


    st.write(
        f"Showing **{len(filtered_df):,}** rows"
    )


    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )


    # =================================================
    # DOWNLOAD FILTERED DATA
    # =================================================

    st.subheader("📥 Export")

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="📥 Download Filtered Data",
        data=csv_data,
        file_name="filtered_data.csv",
        mime="text/csv"
    )


    # =================================================
    # PLOTLY DASHBOARD CHARTS
    # =================================================

    st.subheader("📊 Interactive Dashboard Charts")


    if len(numeric_columns) > 0:

        # =================================================
        # FIND TEXT / CATEGORY COLUMNS
        # =================================================

        text_columns = filtered_df.select_dtypes(
            include=["object", "string", "category"]
        ).columns.tolist()


        # =================================================
        # SELECT NAME / CATEGORY COLUMN
        # =================================================

        if len(text_columns) > 0:

            st.markdown(
                "#### 🏷️ Chart Name / Category"
            )

            name_column = st.selectbox(
                "Choose the column to use as chart labels",
                text_columns,
                index=0,
                key="chart_name_column"
            )

        else:

            name_column = None

            st.warning(
                "No text/category column was found. "
                "Charts will use row numbers."
            )


        # =================================================
        # SELECT NUMERIC COLUMNS
        # =================================================

        st.markdown(
            "#### 🔢 Chart Values"
        )

        numeric_col1, numeric_col2 = st.columns(2)


        with numeric_col1:

            first_column = st.selectbox(
                "First numeric column",
                numeric_columns,
                index=0,
                key="chart_first_column"
            )


        with numeric_col2:

            if len(numeric_columns) >= 2:

                second_column = st.selectbox(
                    "Second numeric column",
                    numeric_columns,
                    index=1,
                    key="chart_second_column"
                )

            else:

                second_column = None

                st.info(
                    "Only one numeric column was found. "
                    "Comparison charts will use only that column."
                )


        # =================================================
        # PREPARE CHART DATA
        # =================================================

        if name_column is not None:

            if second_column is not None:

                chart_data = filtered_df[
                    [
                        name_column,
                        first_column,
                        second_column
                    ]
                ].dropna()

            else:

                chart_data = filtered_df[
                    [
                        name_column,
                        first_column
                    ]
                ].dropna()

        else:

            if second_column is not None:

                chart_data = filtered_df[
                    [
                        first_column,
                        second_column
                    ]
                ].dropna()

            else:

                chart_data = filtered_df[
                    [
                        first_column
                    ]
                ].dropna()


            chart_data = chart_data.reset_index(
                drop=True
            )


            chart_data.insert(
                0,
                "Record",
                [
                    f"Record {i + 1}"
                    for i in range(len(chart_data))
                ]
            )


            name_column = "Record"


        # =================================================
        # LIMIT CHART DATA
        # =================================================

        chart_data = chart_data.head(20)


        # =================================================
        # ROW 1
        # =================================================

        chart_col1, chart_col2 = st.columns(2)


        # =================================================
        # 2D CLUSTERED BAR
        # =================================================

        with chart_col1:

            st.markdown(
                "### 📊 2D Clustered Bar"
            )


            if len(chart_data) > 0:

                if second_column is not None:

                    bar_data = chart_data.melt(
                        id_vars=[name_column],
                        value_vars=[
                            first_column,
                            second_column
                        ],
                        var_name="Metric",
                        value_name="Value"
                    )


                    fig_bar = px.bar(
                        bar_data,
                        x="Value",
                        y=name_column,
                        color="Metric",
                        barmode="group",
                        orientation="h",
                        title=(
                            f"{first_column} vs "
                            f"{second_column}"
                        ),
                        labels={
                            "Value": "Value",
                            name_column: name_column,
                            "Metric": "Metric"
                        },
                        hover_data={
                            name_column: True,
                            "Metric": True,
                            "Value": True
                        }
                    )

                else:

                    fig_bar = px.bar(
                        chart_data,
                        x=first_column,
                        y=name_column,
                        orientation="h",
                        title=(
                            f"{first_column} by "
                            f"{name_column}"
                        ),
                        labels={
                            first_column: first_column,
                            name_column: name_column
                        }
                    )


                fig_bar.update_layout(
                    height=450,
                    hovermode="closest"
                )


                st.plotly_chart(
                    fig_bar,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No data available for the bar chart."
                )


        # =================================================
        # CLUSTERED COLUMN
        # =================================================

        with chart_col2:

            st.markdown(
                "### 📊 Clustered Column"
            )


            if len(chart_data) > 0:

                if second_column is not None:

                    column_data = chart_data.melt(
                        id_vars=[name_column],
                        value_vars=[
                            first_column,
                            second_column
                        ],
                        var_name="Metric",
                        value_name="Value"
                    )


                    fig_column = px.bar(
                        column_data,
                        x=name_column,
                        y="Value",
                        color="Metric",
                        barmode="group",
                        title=(
                            f"{first_column} vs "
                            f"{second_column}"
                        ),
                        labels={
                            name_column: name_column,
                            "Value": "Value",
                            "Metric": "Metric"
                        },
                        hover_data={
                            name_column: True,
                            "Metric": True,
                            "Value": True
                        }
                    )

                else:

                    fig_column = px.bar(
                        chart_data,
                        x=name_column,
                        y=first_column,
                        title=(
                            f"{first_column} by "
                            f"{name_column}"
                        ),
                        labels={
                            name_column: name_column,
                            first_column: first_column
                        }
                    )


                fig_column.update_layout(
                    height=450,
                    hovermode="closest"
                )


                st.plotly_chart(
                    fig_column,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No data available for the column chart."
                )


        # =================================================
        # ROW 2
        # =================================================

        chart_col3, chart_col4 = st.columns(2)


        # =================================================
        # DOUGHNUT CHART
        # =================================================

        with chart_col3:

            st.markdown(
                "### 🍩 Doughnut Chart"
            )


            if len(chart_data) > 0:

                # -----------------------------------------
                # IMPORTANT FIX
                # -----------------------------------------
                # Only use ONE numeric column.
                # This prevents errors such as:
                #
                # DuplicateError:
                # Expected unique column names,
                # got: 'Sales' 2 times
                # -----------------------------------------

                doughnut_data = chart_data[
                    [
                        name_column,
                        first_column
                    ]
                ].copy()


                # Rename columns so Plotly always
                # receives unique names.

                doughnut_data.columns = [
                    "Category",
                    "Value"
                ]


                # Convert values to numeric

                doughnut_data["Value"] = pd.to_numeric(
                    doughnut_data["Value"],
                    errors="coerce"
                )


                # Remove invalid values

                doughnut_data = doughnut_data.dropna(
                    subset=["Category", "Value"]
                )


                # Combine duplicate categories

                doughnut_data = (
                    doughnut_data
                    .groupby(
                        "Category",
                        as_index=False
                    )["Value"]
                    .sum()
                )


                # Sort largest values first

                doughnut_data = doughnut_data.sort_values(
                    "Value",
                    ascending=False
                )


                # Show top 10 categories

                doughnut_data = doughnut_data.head(10)


                if len(doughnut_data) > 0:

                    fig_doughnut = px.pie(
                        doughnut_data,
                        names="Category",
                        values="Value",
                        hole=0.55,
                        title=(
                            f"{first_column} by "
                            f"{name_column}"
                        )
                    )


                    fig_doughnut.update_traces(
                        textposition="inside",
                        textinfo="percent+label",
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Value: %{value:,.2f}<br>"
                            "Share: %{percent}"
                            "<extra></extra>"
                        )
                    )


                    fig_doughnut.update_layout(
                        height=450,
                        showlegend=True
                    )


                    st.plotly_chart(
                        fig_doughnut,
                        use_container_width=True
                    )

                else:

                    st.warning(
                        "No valid data available for "
                        "the doughnut chart."
                    )

            else:

                st.warning(
                    "No data available for the doughnut chart."
                )


        # =================================================
        # LINE CHART WITH MARKERS
        # =================================================

        with chart_col4:

            st.markdown(
                "### 📈 2D Line with Markers"
            )


            if len(chart_data) > 0:

                line_data = chart_data[
                    [
                        name_column,
                        first_column
                    ]
                ].copy()


                fig_line = px.line(
                    line_data,
                    x=name_column,
                    y=first_column,
                    markers=True,
                    title=(
                        f"{first_column} by "
                        f"{name_column}"
                    ),
                    labels={
                        name_column: name_column,
                        first_column: first_column
                    }
                )


                fig_line.update_traces(
                    marker=dict(
                        size=9
                    ),
                    line=dict(
                        width=3
                    ),
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        f"{first_column}: "
                        "%{y:,.2f}"
                        "<extra></extra>"
                    )
                )


                fig_line.update_layout(
                    height=450,
                    hovermode="x unified"
                )


                st.plotly_chart(
                    fig_line,
                    use_container_width=True
                )

            else:

                st.warning(
                    "No data available for the line chart."
                )


    else:

        st.warning(
            "⚠️ No numeric columns were found. "
            "Charts require numeric data."
        )


    # =====================================================
    # NUMERIC ANALYSIS
    # =====================================================

    if len(numeric_columns) > 0:

        st.subheader(
            "📈 Interactive Numeric Analysis"
        )


        selected_column = st.selectbox(
            "Select a numeric column",
            numeric_columns,
            key="analysis_column"
        )


        selected_data = filtered_df[
            selected_column
        ].dropna()


        metric1, metric2, metric3, metric4 = st.columns(4)


        with metric1:

            st.metric(
                "Total",
                f"{selected_data.sum():,.2f}"
            )


        with metric2:

            st.metric(
                "Average",
                f"{selected_data.mean():,.2f}"
            )


        with metric3:

            st.metric(
                "Highest",
                f"{selected_data.max():,.2f}"
            )


        with metric4:

            st.metric(
                "Lowest",
                f"{selected_data.min():,.2f}"
            )


        # =================================================
        # DETAILED STATISTICS
        # =================================================

        st.subheader(
            f"📋 Detailed Statistics - {selected_column}"
        )


        statistics = pd.DataFrame({

            "Metric": [
                "Count",
                "Total",
                "Average",
                "Median",
                "Minimum",
                "Maximum",
                "Standard Deviation"
            ],

            "Value": [
                selected_data.count(),
                selected_data.sum(),
                selected_data.mean(),
                selected_data.median(),
                selected_data.min(),
                selected_data.max(),
                selected_data.std()
            ]

        })


        st.dataframe(
            statistics,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # MISSING DATA ANALYSIS
    # =====================================================

    st.subheader(
        "🔍 Missing Data Analysis"
    )


    missing_data = pd.DataFrame({

        "Column": filtered_df.columns,

        "Missing Values":
            filtered_df.isnull().sum().values

    })


    missing_data["Missing %"] = (
        missing_data["Missing Values"]
        / max(len(filtered_df), 1)
        * 100
    )


    st.dataframe(
        missing_data,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # AUTOMATIC INSIGHTS
    # =====================================================

    st.subheader(
        "🤖 Automatic Insights"
    )


    for column in numeric_columns:

        data = filtered_df[
            column
        ].dropna()


        if len(data) == 0:

            continue


        total = data.sum()

        average = data.mean()

        maximum = data.max()

        minimum = data.min()


        st.info(
            f"**{column}** — "
            f"Total: **{total:,.2f}** | "
            f"Average: **{average:,.2f}** | "
            f"Maximum: **{maximum:,.2f}** | "
            f"Minimum: **{minimum:,.2f}**"
        )


    # =====================================================
    # COLUMN INFORMATION
    # =====================================================

    st.subheader(
        "🧩 Column Information"
    )


    column_info = pd.DataFrame({

        "Column": df.columns,

        "Data Type": [
            str(dtype)
            for dtype in df.dtypes
        ],

        "Non-Empty Values": [
            df[column].notna().sum()
            for column in df.columns
        ],

        "Missing Values": [
            df[column].isna().sum()
            for column in df.columns
        ]

    })


    st.dataframe(
        column_info,
        use_container_width=True,
        hide_index=True
    )


else:

    # =================================================
    # WELCOME SCREEN
    # =================================================

    st.info(
        "👆 Upload an Excel file above to start "
        "the interactive dashboard."
    )


    st.markdown("""
    ### 📊 What this dashboard can do

    **📌 Dashboard Overview**
    - Total rows
    - Total columns
    - Numeric columns
    - Missing values

    **🔎 Interactive Filtering**
    - Filter categories
    - Search the dataset
    - Reset filters

    **📊 Plotly Interactive Charts**
    - 2D Clustered Bar
    - Clustered Column
    - Doughnut Chart
    - 2D Line with Markers
    - Hover information
    - Zoom
    - Pan
    - Interactive legends

    **📈 Numeric Analysis**
    - Total
    - Average
    - Median
    - Minimum
    - Maximum
    - Standard deviation

    **📥 Data Tools**
    - Interactive data table
    - Download filtered data
    - Missing-data report
    - Column information

    **🤖 Automatic Insights**
    - Automatically summarizes numeric columns
    """)