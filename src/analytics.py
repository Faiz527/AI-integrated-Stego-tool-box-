"""
Analytics Module
================
Handles statistics collection, data visualization, and chart generation.
Connected to PostgreSQL database for real user statistics tracking.
"""

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from .db_utils import (
    get_db_connection,
    get_operation_stats,
    get_timeline_data,
    get_method_distribution,
    get_recent_activity
)


# ============================================================================
#                        CHART GENERATION
# ============================================================================

def create_timeline_chart(stats_data=None):
    """Create line chart showing operations timeline over last 7 days."""
    dates, operations = get_timeline_data(days=7)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=operations,
        mode='lines+markers',
        name='Operations',
        line=dict(color='#238636', width=3),
        marker=dict(size=10, color='#238636'),
        fill='tozeroy',
        fillcolor='rgba(35, 134, 54, 0.2)'
    ))
    
    fig.update_layout(
        title="Operations Timeline (Last 7 Days)",
        xaxis_title="Date",
        yaxis_title="Number of Operations",
        hovermode='x unified',
        template='plotly_dark',
        paper_bgcolor='#161B22',
        plot_bgcolor='#0D1117',
        font=dict(color='#C9D1D9'),
        showlegend=False
    )
    
    return fig


def create_method_pie_chart(stats_data=None):
    """Create pie chart showing distribution of steganography methods used."""
    methods, counts = get_method_distribution()
    
    # Map method names for display
    display_methods = {
        'LSB': 'LSB (Spatial Domain)',
        'DCT': 'Hybrid DCT (Y-Channel)',
        'DWT': 'Hybrid DWT (Haar Wavelet)'
    }
    
    display_labels = [display_methods.get(m, m) for m in methods]
    colors = ['#238636', '#1F6FEB', '#DA3633']
    
    fig = go.Figure(data=[go.Pie(
        labels=display_labels,
        values=counts,
        marker=dict(colors=colors[:len(methods)]),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Method Distribution",
        template='plotly_dark',
        paper_bgcolor='#161B22',
        font=dict(color='#C9D1D9')
    )
    
    return fig


def create_encode_decode_chart(stats_data=None):
    """Create bar chart comparing encode vs decode operations."""
    stats = stats_data or get_operation_stats()
    
    if not stats:
        encode_count = 0
        decode_count = 0
    else:
        encode_count = stats['total_encodes']
        decode_count = stats['total_decodes']
    
    categories = ['Encode', 'Decode']
    counts = [encode_count, decode_count]
    colors = ['#238636', '#1F6FEB']
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=counts,
        marker=dict(color=colors),
        text=counts,
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Encode vs Decode Operations",
        xaxis_title="Operation Type",
        yaxis_title="Count",
        template='plotly_dark',
        paper_bgcolor='#161B22',
        plot_bgcolor='#0D1117',
        font=dict(color='#C9D1D9'),
        showlegend=False
    )
    
    return fig


def create_method_comparison_chart(stats_data=None):
    """Create bar chart comparing all three methods."""
    methods, counts = get_method_distribution()
    
    # Map display names
    display_methods = {
        'LSB': 'LSB\n(Spatial)',
        'DCT': 'Hybrid DCT\n(Y-Channel)',
        'DWT': 'Hybrid DWT\n(Wavelet)'
    }
    
    display_labels = [display_methods.get(m, m) for m in methods]
    colors = ['#238636', '#1F6FEB', '#DA3633']
    
    fig = go.Figure(data=[go.Bar(
        x=display_labels,
        y=counts,
        marker=dict(color=colors[:len(methods)]),
        text=counts,
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Method Usage Comparison",
        xaxis_title="Steganography Method",
        yaxis_title="Number of Operations",
        template='plotly_dark',
        paper_bgcolor='#161B22',
        plot_bgcolor='#0D1117',
        font=dict(color='#C9D1D9'),
        showlegend=False
    )
    
    return fig


def create_encryption_chart(stats_data=None):
    """Create pie chart showing encrypted vs unencrypted messages."""
    stats = stats_data or get_operation_stats()
    
    if not stats:
        encrypted = 0
        unencrypted = 0
    else:
        encrypted = stats['encrypted_count']
        unencrypted = stats['total_operations'] - encrypted
    
    labels = ['Encrypted', 'Unencrypted']
    values = [encrypted, unencrypted]
    colors = ['#238636', '#9E6A03']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hoverinfo='label+value+percent'
    )])
    
    fig.update_layout(
        title="Message Encryption Usage",
        template='plotly_dark',
        paper_bgcolor='#161B22',
        font=dict(color='#C9D1D9')
    )
    
    return fig


def create_size_distribution_chart(stats_data=None):
    """Create chart showing data size distribution of operations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query data size distribution with simpler logic
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN data_size IS NULL OR data_size = 0 THEN '< 1 KB'
                    WHEN data_size < 1024 THEN '< 1 KB'
                    WHEN data_size < 1024*1024 THEN '1 KB - 1 MB'
                    WHEN data_size < 10*1024*1024 THEN '1 MB - 10 MB'
                    ELSE '> 10 MB'
                END as size_range,
                COUNT(*) as count
            FROM operations
            WHERE data_size IS NOT NULL
            GROUP BY size_range
            ORDER BY 
                CASE size_range
                    WHEN '< 1 KB' THEN 1
                    WHEN '1 KB - 1 MB' THEN 2
                    WHEN '1 MB - 10 MB' THEN 3
                    WHEN '> 10 MB' THEN 4
                    ELSE 5
                END
        """)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if results:
            ranges = [row[0] for row in results]
            counts = [row[1] for row in results]
        else:
            # Default empty data
            ranges = ['< 1 KB', '1 KB - 1 MB', '1 MB - 10 MB', '> 10 MB']
            counts = [0, 0, 0, 0]
        
        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=ranges,
            y=counts,
            marker=dict(color=['#238636', '#1F6FEB', '#DA3633', '#9E6A03']),
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Operations: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Data Size Distribution",
            xaxis_title="Size Range",
            yaxis_title="Number of Operations",
            template='plotly_dark',
            paper_bgcolor='#161B22',
            plot_bgcolor='#0D1117',
            font=dict(color='#C9D1D9', size=12),
            showlegend=False,
            hovermode='closest',
            height=400
        )
        
        return fig
    
    except Exception as e:
        print(f"❌ Error creating size distribution chart: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a placeholder figure
        fig = go.Figure()
        fig.add_bar(
            x=['< 1 KB', '1 KB - 1 MB', '1 MB - 10 MB', '> 10 MB'],
            y=[0, 0, 0, 0],
            marker=dict(color='#238636')
        )
        fig.update_layout(
            title="Data Size Distribution (No Data)",
            xaxis_title="Size Range",
            yaxis_title="Number of Operations",
            template='plotly_dark',
            paper_bgcolor='#161B22',
            plot_bgcolor='#0D1117',
            font=dict(color='#C9D1D9'),
            showlegend=False,
            annotations=[dict(
                text="No operation data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#C9D1D9")
            )]
        )
        return fig


# ============================================================================
#                        DATAFRAME GENERATION
# ============================================================================

def get_activity_dataframe(limit=10):
    """Generate activity dataframe for display in table format."""
    operations = get_recent_activity(limit=limit)
    
    if not operations:
        # Return empty dataframe with correct columns
        return pd.DataFrame(columns=['Timestamp', 'Action', 'Method', 'Data Size', 'Encrypted', 'Status'])
    
    data = {
        'Timestamp': [op['timestamp'] for op in operations],
        'Action': [op['action'] for op in operations],
        'Method': [op['method'] for op in operations],
        'Data Size': [op['data_size'] for op in operations],
        'Encrypted': ['🔐 Yes' if op['is_encrypted'] else '❌ No' for op in operations],
        'Status': [op['status'] for op in operations]
    }
    
    return pd.DataFrame(data)


def get_statistics_summary(stats_data=None):
    """
    Generate summary statistics for dashboard.
    
    Returns:
        dict: {
            'total_operations': int,
            'lsb_percentage': float,
            'dct_percentage': float,
            'dwt_percentage': float,
            'encryption_percentage': float
        }
    """
    stats = stats_data or get_operation_stats()
    
    if not stats or stats['total_operations'] == 0:
        return {
            'total_operations': 0,
            'lsb_percentage': 0,
            'dct_percentage': 0,
            'dwt_percentage': 0,
            'encryption_percentage': 0
        }
    
    total = stats['total_operations']
    
    return {
        'total_operations': total,
        'lsb_percentage': round((stats['lsb_count'] / total) * 100, 1),
        'dct_percentage': round((stats['dct_count'] / total) * 100, 1),
        'dwt_percentage': round((stats['dwt_count'] / total) * 100, 1),
        'encryption_percentage': round((stats['encrypted_count'] / total) * 100, 1)
    }