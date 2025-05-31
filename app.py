import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Enhanced data structure - more readable and comprehensive
@st.cache_data
def load_data():
    # Original data from your image, restructured for clarity
    data = {
        'For a specific job opportunity': {
            'Working': 85, 'Studying': 0, 'Applying': 5, 'Stay-at-home': 2, 'Other': 3, 'Left': 4
        },
        'To live with my partner who was living here': {
            'Working': 59, 'Studying': 5, 'Applying': 20, 'Stay-at-home': 5, 'Other': 6, 'Left': 4
        },
        'To study/do research': {
            'Working': 55, 'Studying': 18, 'Applying': 13, 'Stay-at-home': 3, 'Other': 3, 'Left': 9
        },
        'To seek employment': {
            'Working': 53, 'Studying': 0, 'Applying': 23, 'Stay-at-home': 2, 'Other': 3, 'Left': 10
        },
        'My spouse/partner was offered a job': {
            'Working': 48, 'Studying': 4, 'Applying': 22, 'Stay-at-home': 14, 'Other': 6, 'Left': 5
        }
    }
    
    # Convert to DataFrame for easier manipulation
    rows = []
    for original_reason, statuses in data.items():
        for current_status, percentage in statuses.items():
            rows.append({
                'Original Reason': original_reason,
                'Current Status': current_status,
                'Percentage': percentage
            })
    
    return pd.DataFrame(rows), data

# Color scheme - more intuitive colors
STATUS_COLORS = {
    'Working': '#2E8B57',        # Sea Green - positive outcome
    'Studying': '#4169E1',       # Royal Blue - education
    'Applying': '#FF8C00',       # Dark Orange - in transition
    'Stay-at-home': '#9370DB',   # Medium Purple - lifestyle choice
    'Other': '#708090',          # Slate Gray - unclear
    'Left': '#DC143C'            # Crimson - negative outcome
}

REASON_COLORS = {
    'For a specific job opportunity': STATUS_COLORS['Working'],          # Align with Working
    'To live with my partner who was living here': '#BC8F8F',            # Distinct but muted
    'To study/do research': STATUS_COLORS['Studying'],                   # Align with Studying
    'To seek employment': STATUS_COLORS['Applying'],                     # Align with Applying
    'My spouse/partner was offered a job': '#8B4513'                     # Distinct from 'Stay-at-home' or 'Left'
}


def create_sankey_diagram(data_dict, selected_node=None):
    """Create a Sankey diagram showing flow from reasons to outcomes"""
    
    # Prepare data for Sankey
    reasons = list(data_dict.keys())
    statuses = ['Working', 'Studying', 'Applying', 'Stay-at-home', 'Other', 'Left']
    
    # Create node lists
    source_nodes = reasons
    target_nodes = [f"Now: {status}" for status in statuses]
    all_nodes = source_nodes + target_nodes
    
    # Create links
    source_indices = []
    target_indices = []
    values = []
    colors = []
    
    for i, reason in enumerate(reasons):
        for j, status in enumerate(statuses):
            if data_dict[reason][status] > 0:  # Only include non-zero flows
                source_indices.append(i)
                target_indices.append(len(reasons) + j)
                values.append(data_dict[reason][status])
                
                # Color logic based on selection
                if selected_node is None:
                    # Default: color based on target status
                    colors.append(f"rgba{tuple(list(px.colors.hex_to_rgb(STATUS_COLORS[status])) + [0.6])}")
                else:
                    # Highlight/grey out based on selection
                    if (selected_node == reason or 
                        selected_node == f"Now: {status}" or
                        selected_node == status):
                        # Highlight selected flows
                        colors.append(f"rgba{tuple(list(px.colors.hex_to_rgb(STATUS_COLORS[status])) + [0.8])}")
                    else:
                        # Grey out non-selected flows
                        colors.append("rgba(200, 200, 200, 0.3)")
    
    # Node colors with highlighting
    node_colors = []
    for node in all_nodes:
        if selected_node is None:
            # Default colors
            if node in reasons:
                node_colors.append(REASON_COLORS.get(node, '#808080'))
            else:
                status_name = node.replace('Now: ', '')
                node_colors.append(STATUS_COLORS.get(status_name, '#808080'))
        else:
            # Highlight/grey based on selection
            if (node == selected_node or 
                node == f"Now: {selected_node}" or
                f"Now: {node}" == selected_node):
                # Highlight selected node
                if node in reasons:
                    node_colors.append(REASON_COLORS.get(node, '#808080'))
                else:
                    status_name = node.replace('Now: ', '')
                    node_colors.append(STATUS_COLORS.get(status_name, '#808080'))
            else:
                # Grey out non-selected nodes
                node_colors.append('rgba(200, 200, 200, 0.7)')
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="white", width=2),  # White border for better contrast
            label=all_nodes,
            color=node_colors,
            # Make nodes clickable
            customdata=all_nodes,
        ),
        link=dict(
	    hoverlabel=dict(bgcolor="white"),
            source=source_indices,
            target=target_indices,
            value=values,
            color=colors
        )
    )])
    
    title_text = "Flow from Original Reasons to Current Status"
    if selected_node:
        if selected_node.startswith("Now: "):
            title_text += f" (Highlighting: {selected_node.replace('Now: ', '')})"
        else:
            title_text += f" (Highlighting: {selected_node})"
    
    fig.update_layout(
        title=title_text,
        font_size=12,
        height=600,
        font=dict(color="black", size=14, family="Arial Bold")
  # Apply font styling to the whole figure
    )
    
    return fig

def create_stacked_bar_chart(df):
    pivot_df = df.pivot(index='Original Reason', columns='Current Status', values='Percentage').fillna(0)
    pivot_df = pivot_df.sort_values('Working', ascending=False)

    # Create shortened labels for clarity
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
                text=pivot_df[status].apply(lambda x: f'{x}%' if x > 3 else ''),
                textposition='inside',
                textfont=dict(color='white', size=10, family="Arial Bold")
            ))

    fig.update_layout(
        title="Current Status Distribution by Original Reason (Ordered by Working Rate)",
        xaxis_title="Percentage",
        yaxis_title="Original Reason for Coming to Denmark",
        barmode='stack',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(categoryorder='array', categoryarray=pivot_df.index.tolist())
    )

    return fig




def main():
    st.set_page_config(
        page_title="Danish Journey Analyser",
	page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load data
    df, data_dict = load_data()
    
    # Header
    st.title("🇩🇰 Danish Expat Journey: From Arrival to Reality")
    st.markdown("""
    **Explore how different reasons for moving to Denmark correlate with long-term outcomes.**  
    This interactive analysis reveals patterns in expat integration and success rates.
    """)
    
    # Sidebar controls
    with st.sidebar:
        st.header("Analysis Options")
        
        view_mode = st.selectbox(
            "Choose Analysis View:",
            ["📊 Overview Dashboard", "🌊 Flow Analysis"])
        
  
          
    
    # Main content area
    if view_mode == "📊 Overview Dashboard":
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Current Status Distribution")
            fig_stacked = create_stacked_bar_chart(df)
            st.plotly_chart(fig_stacked, use_container_width=True)
        
        with col2:
            st.subheader("Key Insights")
            
            # Calculate some quick stats
            working_rates = {reason: data_dict[reason]['Working'] for reason in data_dict.keys()}
            best_reason = max(working_rates, key=working_rates.get)
            worst_reason = min(working_rates, key=working_rates.get)
            
            st.metric("Best Integration Rate", f"{working_rates[best_reason]}%", 
                     delta=f"{best_reason}")
            st.metric("Challenging Integration", f"{working_rates[worst_reason]}%", 
                     delta=f"{worst_reason}")
            
            # Average outcomes
            avg_working = np.mean([data_dict[r]['Working'] for r in data_dict.keys()])
            avg_left = np.mean([data_dict[r]['Left'] for r in data_dict.keys()])
            
            st.metric("Average Working Rate", f"{avg_working:.1f}%")
            st.metric("Average Departure Rate", f"{avg_left:.1f}%")
    
    elif view_mode == "🌊 Flow Analysis":
        st.subheader("Journey Flow: From Intention to Reality")
        
        # Interactive selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            filter_options = ["Show All"] + list(data_dict.keys()) + list(STATUS_COLORS.keys())
            selected_filter = st.selectbox(
                "🎯 Focus on specific reason or outcome:",
                filter_options,
                help="Select a category to highlight its flows and grey out others"
            )
        
        # Determine what to highlight
        selected_node = None if selected_filter == "Show All" else selected_filter
        
        fig_sankey = create_sankey_diagram(data_dict, selected_node)
        
        # Display the chart
        sankey_container = st.container()
        with sankey_container:
            st.plotly_chart(fig_sankey, use_container_width=True)
        
        # Add interpretation
        st.markdown("""
        **How to Read This Flow Diagram:**
        - **Left side**: Original reasons for coming to Denmark
        - **Right side**: Current status of those expats
        - **Flow thickness**: Proportion of people following each path
        - **Colors**: Coded by final outcome (Green=Working, Red=Left, etc.)
        - **Interactive**: Use the dropdown above to focus on specific categories!
        """)
        st.markdown("""
        ---
        **💬 Did you know?**  
        People who moved to Denmark *because their partner got a job* are 
        **much less likely to be working**  
        compared to those who *chose to join a partner already living here*.  
        That small difference in starting point shows up in long-term outcomes.
        """)

        
        # Show stats for selected category
        if selected_node and selected_node != "Show All":
            st.markdown("---")
            if selected_node in data_dict:
                # Selected an original reason
                reason_stats = data_dict[selected_node]
                st.subheader(f"📊 Detailed Stats: {selected_node}")
                
                cols = st.columns(len(reason_stats))
                for i, (status, percentage) in enumerate(reason_stats.items()):
                    with cols[i]:
                        color = STATUS_COLORS.get(status, "#808080")
                        st.markdown(
                            f"""<div style="padding: 10px; border-left: 4px solid {color}; background-color: rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.1])};">
                            <strong>{status}</strong><br>{percentage}%</div>""", 
                            unsafe_allow_html=True
                        )
            
            elif selected_node in STATUS_COLORS:
                # Selected a current status
                st.subheader(f"📊 Who ends up '{selected_node}'?")
                status_breakdown = {}
                for reason, outcomes in data_dict.items():
                    if outcomes[selected_node] > 0:
                        status_breakdown[reason] = outcomes[selected_node]
                
                if status_breakdown:
                    sorted_reasons = sorted(status_breakdown.items(), key=lambda x: x[1], reverse=True)
                    for reason, percentage in sorted_reasons:
                        color = REASON_COLORS.get(reason, "#808080")
                        st.markdown(
                            f"""<div style="margin: 5px 0; padding: 8px; border-left: 3px solid {color}; background-color: rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.1])};">
                            <strong>{percentage}%</strong> of people who came for: <em>{reason}</em></div>""", 
                            unsafe_allow_html=True
                        )
    
           
             
    
    # Footer insights
    st.markdown("---")
    st.subheader("💡 Key Takeaways")
    
    col1, col2, col3 = st.columns(3)

    with col1:
    	st.markdown("""
    	**Most Successful Path:**  
    	Coming with a specific job opportunity leads to 85% employment rate – the highest success rate.
    	""")

    with col2:
    	st.markdown("""
    	**Biggest Challenge:**  
    	Job seekers and partner followers face higher application rates, suggesting integration difficulties.
    	""")
    
    	st.markdown("---")

    	st.markdown("""
    	**👀 Surprising Pattern:**  
    	Accompanying spouses (those who came because *their* partner got a job) are 
	**less likely to be working**  
    	than those who **chose to join a partner already living here.**  
    	This suggests job outcomes are mostly shaped by the quality of the network available to a job seeker.
    	""")

    with col3:
    	st.markdown("""
    	**Student Outcomes:**  
    	Study/research path shows good working integration (55%) with natural transition from studying.
    	""")


if __name__ == "__main__":
    main()