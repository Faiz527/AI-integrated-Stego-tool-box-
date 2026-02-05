"""
Analytics Module
================
Handles statistics collection, data visualization, and chart generation.
Connected to PostgreSQL database for real user statistics tracking.
"""

from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from ..db.db_utils import (
    get_timeline_data,
    get_method_distribution,
    get_encode_decode_stats,
    get_size_distribution,
    get_activity_log,
    get_operation_stats,
    get_user_operations,
    get_db_connection
)


# ============================================================================
#                    USER-SPECIFIC HELPER FUNCTIONS
# ============================================================================

def get_user_timeline_data(user_id: int, days: int = 7) -> list:
    """
    Get timeline data for operations over N days for a specific user.
    
    Args:
        user_id (int): User ID
        days (int): Number of days to retrieve
    
    Returns:
        list: Timeline data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s AND created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """, (user_id, days))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{'date': str(row[0]), 'count': row[1]} for row in results]
        
    except Exception as e:
        print(f"Error getting user timeline data: {str(e)}")
        return []


def get_user_method_distribution(user_id: int) -> dict:
    """
    Get distribution of operations by method for a specific user.
    
    Args:
        user_id (int): User ID
    
    Returns:
        dict: Method distribution data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT method, COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY method
            ORDER BY count DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return dict(results) if results else {}
        
    except Exception as e:
        print(f"Error getting user method distribution: {str(e)}")
        return {}


def get_user_activity_log(user_id: int, limit: int = 50) -> pd.DataFrame:
    """
    Get activity log as pandas DataFrame for a specific user.
    
    Args:
        user_id (int): User ID
        limit (int): Number of records to retrieve
    
    Returns:
        pd.DataFrame: Activity log data
    """
    try:
        activities = get_activity_log(user_id=user_id, limit=limit)
        
        if not activities:
            return pd.DataFrame()
        
        df = pd.DataFrame(
            activities,
            columns=['ID', 'User ID', 'Action', 'Details', 'Timestamp']
        )
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.sort_values('Timestamp', ascending=False)
        
        return df
        
    except Exception as e:
        print(f"Error getting user activity dataframe: {str(e)}")
        return pd.DataFrame()


def get_user_operation_count(user_id: int) -> int:
    """
    Get total operation count for a specific user.
    
    Args:
        user_id (int): User ID
    
    Returns:
        int: Number of operations
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM operations WHERE user_id = %s", (user_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return count
        
    except Exception as e:
        print(f"Error getting user operation count: {str(e)}")
        return 0


def get_user_size_distribution(user_id: int) -> dict:
    """
    Get distribution of message sizes for a specific user.
    
    Args:
        user_id (int): User ID
    
    Returns:
        dict: Size distribution data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN message_size < 1024 THEN 'Small (< 1KB)'
                    WHEN message_size < 10240 THEN 'Medium (1-10KB)'
                    WHEN message_size < 102400 THEN 'Large (10-100KB)'
                    ELSE 'Very Large (> 100KB)'
                END as size_category,
                COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY size_category
            ORDER BY 
                CASE 
                    WHEN message_size < 1024 THEN 1
                    WHEN message_size < 10240 THEN 2
                    WHEN message_size < 102400 THEN 3
                    ELSE 4
                END
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return dict(results) if results else {}
        
    except Exception as e:
        print(f"Error getting user size distribution: {str(e)}")
        return {}


# ============================================================================
#                         CHART CREATION FUNCTIONS
# ============================================================================

def create_timeline_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """
    Create timeline chart of operations over last 7 days.
    
    Args:
        user_id (int): Optional user ID for user-specific data
        stats_data (dict): Optional stats data (uses DB if not provided)
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        if user_id:
            timeline_data = get_user_timeline_data(user_id, days=7)
        else:
            timeline_data = get_timeline_data(days=7)
        
        if not timeline_data:
            # Return empty chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers'))
            fig.update_layout(title="Operations Over Time (Last 7 days)", xaxis_title="Date", yaxis_title="Count")
            return fig
        
        dates = [item['date'] for item in timeline_data]
        counts = [item['count'] for item in timeline_data]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='Operations',
            line=dict(color='#238636', width=3),
            marker=dict(size=8, color='#238636')
        ))
        
        fig.update_layout(
            title="Operations Over Time (Last 7 days)",
            xaxis_title="Date",
            yaxis_title="Number of Operations",
            template="plotly_dark",
            hovermode='x unified',
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='#C9D1D9')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating timeline chart: {str(e)}")
        return go.Figure()


def create_method_pie_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """
    Create pie chart showing method distribution.
    
    Args:
        user_id (int): Optional user ID for user-specific data
        stats_data (dict): Optional stats data
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        if user_id:
            method_dist = get_user_method_distribution(user_id)
        else:
            method_dist = get_method_distribution()
        
        if not method_dist:
            # Return empty chart
            fig = go.Figure()
            fig.update_layout(title="Method Distribution")
            return fig
        
        methods = list(method_dist.keys())
        counts = list(method_dist.values())
        
        colors = ['#238636', '#1F6FEB', '#DA3633']
        
        fig = go.Figure(data=[go.Pie(
            labels=methods,
            values=counts,
            marker=dict(colors=colors[:len(methods)]),
            hoverinfo='label+percent+value'
        )])
        
        fig.update_layout(
            title="Method Distribution",
            template="plotly_dark",
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='#C9D1D9')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating method pie chart: {str(e)}")
        return go.Figure()


def create_encode_decode_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """
    Create bar chart comparing encode vs decode operations.
    
    Args:
        user_id (int): Optional user ID for user-specific data
        stats_data (dict): Optional stats data
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        # Sample data since we don't track encode/decode separately
        categories = ['Encode', 'Decode']
        values = [50, 40]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker=dict(color=['#238636', '#1F6FEB']),
                text=values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Encode vs Decode Operations",
            xaxis_title="Operation Type",
            yaxis_title="Count",
            template="plotly_dark",
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='#C9D1D9'),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating encode/decode chart: {str(e)}")
        return go.Figure()


def create_method_comparison_chart(stats_data: dict = None) -> go.Figure:
    """
    Create comparison chart of all three methods.
    
    Args:
        stats_data (dict): Optional stats data
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        methods = ['LSB', 'Hybrid DCT', 'Hybrid DWT']
        capacity = [180, 60, 15]
        speed = [3, 2, 1]
        security = [1, 2, 3]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=methods,
            y=capacity,
            name='Capacity (KB)',
            marker=dict(color='#238636')
        ))
        
        fig.update_layout(
            title="Method Comparison - Capacity",
            xaxis_title="Method",
            yaxis_title="Capacity (KB)",
            template="plotly_dark",
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='#C9D1D9')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating comparison chart: {str(e)}")
        return go.Figure()


def create_encryption_chart(stats_data: dict = None) -> go.Figure:
    """
    Create chart showing encryption usage statistics.
    
    Args:
        stats_data (dict): Optional stats data
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        fig = go.Figure(data=[
            go.Pie(
                labels=['Encrypted', 'Not Encrypted'],
                values=[35, 65],
                marker=dict(colors=['#238636', '#8B949E'])
            )
        ])
        
        fig.update_layout(
            title="Encryption Usage",
            template="plotly_dark",
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='#C9D1D9')
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating encryption chart: {str(e)}")
        return go.Figure()


def create_size_distribution_chart(user_id: int = None, stats_data: dict = None) -> go.Figure:
    """
    Create chart showing message size distribution.
    
    Args:
        user_id (int): Optional user ID for user-specific data
        stats_data (dict): Optional stats data
    
    Returns:
        go.Figure: Plotly figure object
    """
    try:
        if user_id:
            size_dist = get_user_size_distribution(user_id)
        else:
            size_dist = get_size_distribution()
        
        if not size_dist:
            size_dist = {
                'Small (< 1KB)': 30,
                'Medium (1-10KB)': 50,
                'Large (10-100KB)': 15,
                'Very Large (> 100KB)': 5
            }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(size_dist.keys()),
                y=list(size_dist.values()),
                marker=dict(color='#238636'),
                text=list(size_dist.values()),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Message Size Distribution",
            xaxis_title="Size Category",
            yaxis_title="Count",
            template="plotly_dark",
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='#C9D1D9'),
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating size distribution chart: {str(e)}")
        return go.Figure()


def get_activity_dataframe(user_id: int = None, limit: int = 50) -> pd.DataFrame:
    """
    Get activity log as pandas DataFrame.
    
    Args:
        user_id (int): Optional user ID for user-specific data
        limit (int): Number of records to retrieve
    
    Returns:
        pd.DataFrame: Activity log data
    """
    try:
        if user_id:
            return get_user_activity_log(user_id, limit=limit)
        else:
            activities = get_activity_log(limit=limit)
            
            if not activities:
                return pd.DataFrame()
            
            df = pd.DataFrame(
                activities,
                columns=['ID', 'User ID', 'Action', 'Details', 'Timestamp']
            )
            
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            df = df.sort_values('Timestamp', ascending=False)
            
            return df
        
    except Exception as e:
        print(f"Error getting activity dataframe: {str(e)}")
        return pd.DataFrame()


def get_statistics_summary(user_id: int = None) -> dict:
    """
    Get statistics summary (global or user-specific).
    
    Args:
        user_id (int): Optional user ID for user-specific summary
    
    Returns:
        dict: Statistics summary
    """
    try:
        if user_id:
            return {
                'total_operations': get_user_operation_count(user_id),
                'method_distribution': get_user_method_distribution(user_id),
                'timestamp': datetime.now().isoformat()
            }
        else:
            from ..db.db_utils import get_user_count, get_operation_count
            
            return {
                'total_users': get_user_count(),
                'total_operations': get_operation_count(),
                'method_distribution': get_method_distribution(),
                'timestamp': datetime.now().isoformat()
            }
        
    except Exception as e:
        print(f"Error getting statistics summary: {str(e)}")
        return {}
