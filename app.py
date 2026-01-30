import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Complete data structure with absolute numbers
@st.cache_data
def load_data():
    # Corrected cohort sizes (calculated from the survey data percentages)
    cohort_sizes = {
        'For a specific job opportunity': 475,
        'To live with my partner who was living here': 518,
        'To study/do research': 281,
        'To seek employment': 216,
        'My spouse/partner was offered a job': 367
    }
    
    # Percentage breakdowns within each cohort (from the original data)
    percentage_data = {
        'For a specific job opportunity': {
            'Working': 85, 'Applying': 5, 'Studying': 2,  'Stay-at-home': 2, 'Other': 3, 'Left': 4
        },
        'To live with my partner who was living here': {
            'Working': 59, 'Applying': 20, 'Studying': 5,  'Stay-at-home': 5, 'Other': 6, 'Left': 4
        },
        'To study/do research': {
            'Working': 55, 'Applying': 13, 'Studying': 18,  'Stay-at-home': 1, 'Other': 3, 'Left': 9
        },
        'To seek employment': {
            'Working': 53, 'Applying': 23, 'Studying': 10,  'Stay-at-home': 2, 'Other': 3, 'Left': 10
        },
        'My spouse/partner was offered a job': {
            'Working': 48, 'Applying': 22, 'Studying': 4,  'Stay-at-home': 14, 'Other': 6, 'Left': 5
        }
    }
    
    # Convert percentages to absolute numbers
    absolute_data = {}
    for reason, size in cohort_sizes.items():
        absolute_data[reason] = {}
        for status, percentage in percentage_data[reason].items():
            absolute_data[reason][status] = round(size * percentage / 100)
    
    # Create comprehensive DataFrame
    rows = []
    for original_reason, statuses in percentage_data.items():
        for current_status, percentage in statuses.items():
            absolute_count = absolute_data[original_reason][current_status]
            rows.append({
                'Original Reason': original_reason,
                'Current Status': current_status,
                'Percentage': percentage,
                'Absolute Count': absolute_count,
                'Cohort Size': cohort_sizes[original_reason]
            })
    
    return pd.DataFrame(rows), absolute_data, percentage_data, cohort_sizes

# Color scheme - intuitive and accessible
STATUS_COLORS = {
    'Working': '#2E8B57',        # Sea Green - positive outcome
    'Studying': '#4169E1',       # Royal Blue - education
    'Applying': '#FF8C00',       # Dark Orange - in transition
    'Stay-at-home': '#9370DB',   # Medium Purple - lifestyle choice
    'Other': '#708090',          # Slate Gray - unclear
    'Left': '#DC143C'            # Crimson - negative outcome
}

REASON_COLORS = {
    'For a specific job opportunity': STATUS_COLORS['Working'],
    'To live with my partner who was living here': '#BC8F8F',
    'To study/do research': STATUS_COLORS['Studying'],
    'To seek employment': STATUS_COLORS['Applying'],
    'My spouse/partner was offered a job': '#8B4513'
}

def create_sankey_diagram(absolute_data, cohort_sizes, selected_node=None):
    """Create a Sankey diagram showing absolute flows from reasons to outcomes"""
    
    reasons = list(absolute_data.keys())
    statuses = ['Working', 'Studying', 'Applying', 'Stay-at-home', 'Other', 'Left']
    # Calculate totals for each final status across all cohorts
    status_totals = {}
    for status in statuses:
        total = sum(absolute_data[reason][status] for reason in reasons)        
        status_totals[status] = total


    
    # Create node lists with cohort sizes
    source_nodes = [f"{reason}\n({cohort_sizes[reason]} people in total)" for reason in reasons]
    target_nodes = [f"Now: {status}\n({status_totals[status]} people in total)" for status in statuses]
    all_nodes = source_nodes + target_nodes
    
    # Create links with absolute numbers
    source_indices = []
    target_indices = []
    values = []
    colors = []
    
    for i, reason in enumerate(reasons):
        for j, status in enumerate(statuses):
            count = absolute_data[reason][status]
            if count > 0:  # Only include non-zero flows
                source_indices.append(i)
                target_indices.append(len(reasons) + j)
                values.append(count)
                
                # Color logic based on selection
                if selected_node is None:
                    colors.append(f"rgba{tuple(list(px.colors.hex_to_rgb(STATUS_COLORS[status])) + [0.6])}")
                else:
                    # Check if this flow should be highlighted
                    reason_match = (selected_node == reason or 
                                  selected_node in source_nodes[i])
                    status_match = (selected_node == f"Now: {status}" or 
                                  selected_node == status)
                    
                    if reason_match or status_match:
                        colors.append(f"rgba{tuple(list(px.colors.hex_to_rgb(STATUS_COLORS[status])) + [0.8])}")
                    else:
                        colors.append("rgba(200, 200, 200, 0.3)")
    
    # Node colors with highlighting
    node_colors = []
    for i, node in enumerate(all_nodes):
        if selected_node is None:
            if i < len(reasons):  # Source node
                node_colors.append(REASON_COLORS.get(reasons[i], '#808080'))
            else:  # Target node
                status_name = node.replace('Now: ', '')
                node_colors.append(STATUS_COLORS.get(status_name, '#808080'))
        else:
            # Highlight logic
            should_highlight = False
            if i < len(reasons):  # Source node
                should_highlight = (selected_node == reasons[i] or selected_node in node)
            else:  # Target node
                status_name = node.replace('Now: ', '')
                should_highlight = (selected_node == f"Now: {status_name}" or 
                                  selected_node == status_name)
            
            if should_highlight:
                if i < len(reasons):
                    node_colors.append(REASON_COLORS.get(reasons[i], '#808080'))
                else:
                    status_name = node.replace('Now: ', '')
                    node_colors.append(STATUS_COLORS.get(status_name, '#808080'))
            else:
                node_colors.append('rgba(200, 200, 200, 0.7)')
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=25,
            line=dict(color="white", width=2),
            label=all_nodes,
            color=node_colors,
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=colors,
            # Custom hover text showing absolute numbers
            hovertemplate='%{source.label} → %{target.label}<br>%{value} people<extra></extra>'
        )
    )])
    
    title_text = "Flow from Original Reasons to Current Status (Absolute Numbers)"
    if selected_node:
        title_text += f" (Highlighting: {selected_node})"
    
    fig.update_layout(
        title=title_text,
        height=700,
        font=dict(family="Arial", size=20, color="gray"),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def create_stacked_bar_chart(df, use_absolute=False):
    """Create stacked bar chart with option for absolute or percentage view"""
    
    if use_absolute:
        # Use absolute counts
        pivot_df = df.pivot(index='Original Reason', columns='Current Status', values='Absolute Count').fillna(0)
        title_suffix = "(Absolute Numbers)"
        value_format = lambda x: f'{int(x)}' if x > 5 else ''
        x_title = "Number of People"
    else:
        # Use percentages
        pivot_df = df.pivot(index='Original Reason', columns='Current Status', values='Percentage').fillna(0)
        title_suffix = "(Percentages)"
        value_format = lambda x: f'{x}%' if x > 3 else ''
        x_title = "Percentage"
    
    # Sort by working rate and create short labels
    working_col = 'Working'
    if use_absolute:
        # For absolute numbers, sort by percentage but display absolute
        percentage_pivot = df.pivot(index='Original Reason', columns='Current Status', values='Percentage').fillna(0)
        sort_order = percentage_pivot.sort_values('Working', ascending=True).index
        pivot_df = pivot_df.reindex(sort_order)
    else:
        pivot_df = pivot_df.sort_values('Working', ascending=True)
    
    short_labels = {
        'For a specific job opportunity': 'Job opportunity',
        'To live with my partner who was living here': 'Joined partner',
        'To study/do research': 'Study/research',
        'To seek employment': 'Sought job',
        'My spouse/partner was offered a job': 'Spouse job offer'
    }
    pivot_df.index = pivot_df.index.map(short_labels)

    fig = go.Figure()
    status_order = ['Working', 'Studying', 'Other', 'Stay-at-home', 'Applying', 'Left']
    
    for status in status_order:
        if status in pivot_df.columns:
            fig.add_trace(go.Bar(
                name=status,
                x=pivot_df[status],
                y=pivot_df.index,
                orientation='h',
                marker_color=STATUS_COLORS[status],
                text=pivot_df[status].apply(value_format),
                textposition='inside',
                textfont=dict(color='white', size=10, family="Arial Bold"),
                hovertemplate=f'{status}: %{{x}}<extra></extra>'
            ))

    fig.update_layout(
        title=f"Current Status Distribution by Original Reason {title_suffix}",
        xaxis_title=x_title,
        yaxis_title="Original Reason for Coming to Denmark",
        barmode='stack',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(categoryorder='array', categoryarray=pivot_df.index.tolist())
    )

    return fig

def create_cohort_overview(cohort_sizes, absolute_data):
    """Create an overview chart showing cohort sizes and outcomes"""
    
    # Calculate working counts for each cohort
    cohort_data = []
    for reason, size in cohort_sizes.items():
        working_count = absolute_data[reason]['Working']
        working_rate = round(working_count / size * 100, 1)
        
        cohort_data.append({
            'Reason': reason,
            'Total Size': size,
            'Working Count': working_count,
            'Working Rate': working_rate
        })
    
    cohort_df = pd.DataFrame(cohort_data)
    
    # Create bubble chart
    fig = go.Figure()
    
    for _, row in cohort_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Working Rate']],
            y=[row['Working Count']],
            mode='markers+text',
            marker=dict(
                size=row['Total Size'] / 10,  # Scale bubble size
                color=REASON_COLORS.get(row['Reason'], '#808080'),
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            text=row['Reason'].replace(' who was living here', '').replace('My spouse/partner was offered a job', 'Spouse job'),
            textposition="middle center",
            textfont=dict(size=11, color='black', family="Arial Bold"),
            hovertemplate=f"<b>{row['Reason']}</b><br>" +
                         f"Total cohort: {row['Total Size']} people<br>" +
                         f"Currently working: {row['Working Count']} people<br>" +
                         f"Working rate: {row['Working Rate']}%<extra></extra>",
            showlegend=False
        ))
    
    fig.update_layout(
        title="Cohort Sizes vs Working Outcomes (Bubble size = cohort size)",
        xaxis_title="Working Rate (%)",
        yaxis_title="Number Currently Working",
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def main():
    st.set_page_config(
        page_title="Danish Journey Analyser",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load all data
    df, absolute_data, percentage_data, cohort_sizes = load_data()
    
    # Header
    st.title("🇩🇰 From Arrival to Current Circumstances")
    st.markdown("""
    **Explore how different reasons for moving to Denmark correlate with long-term outcomes.**  
    This interactive analysis reveals patterns in expat integration and success rates using absolute numbers.
    """)
    
    # Key statistics at the top
    col1, col2, col3 = st.columns(3)
    with col1:
        total_original = sum(cohort_sizes.values())
        st.metric("Original Cohorts", f"{total_original:,}", help="Estimated total people in tracked categories. The number is smaller because of rounding, dropping certain categories like refugees out of the analysis and possibly people have multiple motivations for coming to Denmark")
    with col2:
        st.metric("Current Sample", "2,028", help="People currently in Denmark")
    with col3:
        total_working = sum(data['Working'] for data in absolute_data.values())
        st.metric("Currently Working", f"{total_working:,}", help="Total people working across all cohorts")
                
    # Sidebar controls
    with st.sidebar:
        st.header("Analysis Options")
        
        view_mode = st.selectbox(
            "Choose Analysis View:",
            ["📊 Overview Dashboard", "🌊 Flow Analysis", "💡 Cohort Comparison"])
        
        st.markdown("---")
        # Only show the toggle on Overview Dashboard
        if view_mode == "📊 Overview Dashboard":
            show_absolute = st.checkbox("Show absolute numbers", value=True, 
                               help="Toggle between absolute counts and percentages")
        else:
            show_absolute = True  # Default to True for other views    
    # Main content area
    if view_mode == "📊 Overview Dashboard":
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Current Status Distribution")
            fig_stacked = create_stacked_bar_chart(df, use_absolute=show_absolute)
            st.plotly_chart(fig_stacked, use_container_width=True)
        
        with col2:
            st.subheader("Key Insights")
            
            # Cohort size insights
            largest_cohort = max(cohort_sizes, key=cohort_sizes.get)
            smallest_cohort = min(cohort_sizes, key=cohort_sizes.get)
            
            st.metric("Largest Cohort", f"{cohort_sizes[largest_cohort]} people", 
                     help=f"{largest_cohort}")
            st.metric("Smallest Cohort", f"{cohort_sizes[smallest_cohort]} people", 
                     help=f"{smallest_cohort}")
            
                       
            # Overall statistics
            st.markdown("---")
            st.markdown("**Overall Sample (n=2,028)**")
            st.markdown("• Working: 68% (1,380 people)")
            st.markdown("• Applying: 14% (284 people)")
            st.markdown("• Studying: 7% (142 people)")
            st.markdown("• Stay-at-home: 4% (81 people)")
            st.markdown("• Other: 6% (122 people)")
    
    elif view_mode == "🌊 Flow Analysis":
        st.subheader("Journey Flow: From Intention to Reality")
        
        # Interactive selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            filter_options = ["Show All"] + list(cohort_sizes.keys()) + list(STATUS_COLORS.keys())
            selected_filter = st.selectbox(
                "🎯 Focus on specific reason or outcome:",
                filter_options,
                help="Select a category to highlight its flows and grey out others"
            )
        
        # Determine what to highlight
        selected_node = None if selected_filter == "Show All" else selected_filter
        
        fig_sankey = create_sankey_diagram(absolute_data, cohort_sizes, selected_node)
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        # Add interpretation
        st.markdown("""
        **How to Read This Flow Diagram:**
        - **Left side**: Original reasons for coming to Denmark (with cohort sizes)
        - **Right side**: Current status of those expats
        - **Flow thickness**: Number of people following each path
        - **Colors**: Coded by final outcome (Green=Working, Red=Left, etc.)
        - **Hover**: See exact numbers for each flow
        """)
        
        # Show detailed stats for selected category
        if selected_node and selected_node != "Show All":
            st.markdown("---")
            if selected_node in absolute_data:
                # Selected an original reason
                reason_stats = absolute_data[selected_node]
                cohort_size = cohort_sizes[selected_node]
                st.subheader(f"📊 Detailed Breakdown: {selected_node}")
                st.markdown(f"**Original cohort size**: {cohort_size:,} people")
                
                # Create columns for each status
                status_cols = st.columns(len(reason_stats))
                for i, (status, count) in enumerate(reason_stats.items()):
                    with status_cols[i]:
                        percentage = round(count / cohort_size * 100, 1) if cohort_size > 0 else 0
                        color = STATUS_COLORS.get(status, "#808080")
                        
                        st.markdown(
                            f"""<div style="padding: 15px; border-left: 4px solid {color}; 
                            background-color: rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.1])}; 
                            border-radius: 5px; margin: 5px 0;">
                            <strong>{status}</strong><br>
                            <span style="font-size: 20px;">{count:,} people</span><br>
                            <span style="color: gray;">({percentage}%)</span>
                            </div>""", 
                            unsafe_allow_html=True
                        )
            
            elif selected_node in STATUS_COLORS:
                # Selected a current status
                st.subheader(f"📊 Who ends up '{selected_node}'?")
                status_breakdown = {}
                total_in_status = 0
                
                for reason, outcomes in absolute_data.items():
                    if outcomes[selected_node] > 0:
                        status_breakdown[reason] = outcomes[selected_node]
                        total_in_status += outcomes[selected_node]
                
                if status_breakdown:
                    st.markdown(f"**Total people currently '{selected_node}'**: {total_in_status:,}")
                    
                    sorted_reasons = sorted(status_breakdown.items(), key=lambda x: x[1], reverse=True)
                    for reason, count in sorted_reasons:
                        color = REASON_COLORS.get(reason, "#808080")
                        cohort_size = cohort_sizes[reason]
                        percentage_of_cohort = round(count / cohort_size * 100, 1) if cohort_size > 0 else 0
                        percentage_of_status = round(count / total_in_status * 100, 1) if total_in_status > 0 else 0
                        
                        st.markdown(
                            f"""<div style="margin: 10px 0; padding: 12px; border-left: 3px solid {color}; 
                            background-color: rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.1])}; 
                            border-radius: 5px;">
                            <strong>{count:,} people ({percentage_of_status}% of all {selected_node})</strong><br>
                            From: <em>{reason}</em><br>
                            <small>({percentage_of_cohort}% of that cohort)</small>
                            </div>""", 
                            unsafe_allow_html=True
                        )
    
    elif view_mode == "💡 Cohort Comparison":
        st.subheader("Cohort Size vs Outcomes Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_bubble = create_cohort_overview(cohort_sizes, absolute_data)
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        with col2:
            st.markdown("### Cohort Analysis")
            
            # Create summary table
            summary_data = []
            for reason, size in cohort_sizes.items():
                working_count = absolute_data[reason]['Working']
                left_count = absolute_data[reason]['Left']
                applying_count = absolute_data[reason]['Applying']
                
                summary_data.append({
                    'Reason': reason.replace('To live with my partner who was living here', 'Join partner')
                             .replace('For a specific job opportunity', 'Job opportunity')
                             .replace('My spouse/partner was offered a job', 'Spouse job offer'),
                    'Total': size,
                    'Working': working_count,
                    'Applying': applying_count,
                    'Left DK': left_count,
                    'Success Rate': f"{round(working_count/size*100, 1)}%"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            st.markdown("### Key Patterns")
            st.markdown("""
            **Size vs Success**: Larger cohorts don't necessarily have better outcomes.
            
            **Job Opportunity** (475 people): Highest success rate at 85% working.
            
            **Partner Join** (518 people): Largest cohort, moderate success at 59% working.
            
            **Spouse Job** (367 people): Lowest working rate at 48%, highest stay-at-home rate.
            """)
    
    # Footer insights
    st.markdown("---")
    st.subheader("💡 Key Takeaways")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        job_opp_working = absolute_data['For a specific job opportunity']['Working']
        job_opp_total = cohort_sizes['For a specific job opportunity']
        st.markdown(f"""
        **Most Successful Path:**  
        Coming with a specific job opportunity: **{job_opp_working} out of {job_opp_total} people** (85%) 
        are currently working – the highest success rate.
        """)
    
    with col2:
        partner_working = absolute_data['To live with my partner who was living here']['Working']
        partner_total = cohort_sizes['To live with my partner who was living here']
        spouse_working = absolute_data['My spouse/partner was offered a job']['Working']
        spouse_total = cohort_sizes['My spouse/partner was offered a job']
        
        st.markdown(f"""
        **Partnership Paradox:**  
        **Joining partner already here**: {partner_working}/{partner_total} working (59%)  
        **Following spouse's job**: {spouse_working}/{spouse_total} working (48%)  
        
        *Network quality matters more than just having a partner*
        """)
    
    with col3:
        study_working = absolute_data['To study/do research']['Working']
        study_total = cohort_sizes['To study/do research']
        study_studying = absolute_data['To study/do research']['Studying']
        
        st.markdown(f"""
        **Education Path:**  
        Study/research cohort ({study_total} people):  
        • {study_working} working (55%)  
        • {study_studying} still studying (18%)  
        • Strong pipeline effect
        """)

# === WATERMARK/FOOTER ===
    st.markdown("---")
    st.markdown(
        """
        <div style='
            text-align: center; 
            padding: 20px; 
            margin-top: 30px;
            background: linear-gradient(135deg, #2E8B57 0%, #4169E1 100%);
            border-radius: 10px;
            color: white;
        '>
            <p style='margin: 0; font-size: 14px;'>
                📊 Brought to you by <strong>Fair & Fornuftig</strong>
            </p>
            <p style='margin: 8px 0 0 0; font-size: 12px; opacity: 0.9;'>
                Data source: Copenhagen Capacity Expat Survey 2025 (Pages 35-36)
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
