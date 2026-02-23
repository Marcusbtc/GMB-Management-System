import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def plot_top_keywords(df):
    """Plots top search keywords."""
    if df.empty:
        st.warning("No keyword data available.")
        return None
    
    fig = px.bar(df.head(10), x='count', y='keyword', orientation='h',
                 title='Top 10 Search Keywords',
                 text='display_count',
                 labels={'count': 'Searches (Approx)', 'keyword': 'Keyword'},
                 template='plotly_white')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def plot_metrics_over_time(df):
    """Plots views and actions over time."""
    if df.empty:
        st.warning("No data available to plot.")
        return None
    
    fig = px.line(df, x='date', y=['views', 'actions', 'searches'], 
                  title='Performance Over Time',
                  labels={'value': 'Count', 'date': 'Date', 'variable': 'Metric'},
                  template='plotly_white')
    fig.update_layout(hovermode="x unified")
    return fig

def plot_platform_breakdown(df):
    """Plots platform and device breakdown."""
    if df.empty:
        return None
    
    # Aggregate totals
    totals = {
        "Google Search - Mobile": df['BUSINESS_IMPRESSIONS_MOBILE_SEARCH'].sum(),
        "Google Maps - Mobile": df['BUSINESS_IMPRESSIONS_MOBILE_MAPS'].sum(),
        "Google Search - Desktop": df['BUSINESS_IMPRESSIONS_DESKTOP_SEARCH'].sum(),
        "Google Maps - Desktop": df['BUSINESS_IMPRESSIONS_DESKTOP_MAPS'].sum()
    }
    
    # Filter out zero values
    data = {k: v for k, v in totals.items() if v > 0}
    
    if not data:
        st.warning("No impression data available for breakdown.")
        return None
        
    fig = px.pie(
        values=list(data.values()),
        names=list(data.keys()),
        title="How people discovered your business",
        hole=0.4,
        template='plotly_white'
    )
    return fig

def display_metrics_cards(df):
    """Displays detailed summary metrics cards."""
    if df.empty:
        return
    
    # Calculate Totals
    total_views = (
        df['BUSINESS_IMPRESSIONS_DESKTOP_MAPS'].sum() +
        df['BUSINESS_IMPRESSIONS_DESKTOP_SEARCH'].sum() +
        df['BUSINESS_IMPRESSIONS_MOBILE_MAPS'].sum() +
        df['BUSINESS_IMPRESSIONS_MOBILE_SEARCH'].sum()
    )
    
    total_actions = (
        df['WEBSITE_CLICKS'].sum() +
        df['CALL_CLICKS'].sum() +
        df['BUSINESS_DIRECTION_REQUESTS'].sum() +
        df['BUSINESS_CONVERSATIONS'].sum() +
        df['BUSINESS_BOOKINGS'].sum()
    )
    
    st.subheader("Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total Views", f"{total_views:,}")
    col2.metric("Total Interactions", f"{total_actions:,}")
    
    st.markdown("---")
    st.subheader("Interaction Details")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Website Clicks", f"{int(df['WEBSITE_CLICKS'].sum()):,}")
    c2.metric("Calls", f"{int(df['CALL_CLICKS'].sum()):,}")
    c3.metric("Directions", f"{int(df['BUSINESS_DIRECTION_REQUESTS'].sum()):,}")
    c4.metric("Messages", f"{int(df['BUSINESS_CONVERSATIONS'].sum()):,}")
    c5.metric("Bookings", f"{int(df['BUSINESS_BOOKINGS'].sum()):,}")

def plot_review_sentiment(reviews):
    """Plots review sentiment analysis."""
    if not reviews:
        return None
        
    import pandas as pd
    
    # Extract ratings
    ratings = [r.get('starRating', 'Unknown') for r in reviews]
    rating_counts = pd.Series(ratings).value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    
    # Map string ratings to numbers for better sorting if needed, or keep as is
    # API returns 'FIVE', 'FOUR', etc.
    
    fig = px.pie(
        rating_counts,
        values='Count',
        names='Rating',
        title="Review Ratings Distribution",
        color='Rating',
        color_discrete_map={
            'FIVE': '#4CAF50',
            'FOUR': '#8BC34A',
            'THREE': '#FFC107',
            'TWO': '#FF9800',
            'ONE': '#F44336',
            'Unknown': '#9E9E9E'
        },
        template='plotly_white'
    )
    return fig

def plot_post_performance(posts):
    """Plots performance of local posts."""
    if not posts:
        return None
        
    import pandas as pd
    
    post_data = []
    for p in posts:
        post_data.append({
            'topicType': p.get('topicType', 'UNKNOWN'),
            'state': p.get('state', 'UNKNOWN'),
            'createTime': p.get('createTime')
        })
        
    df = pd.DataFrame(post_data)
    if df.empty:
        return None
        
    fig = px.histogram(df, x='topicType', color='state', 
                       title="Posts by Type and State",
                       template='plotly_white')
    return fig
