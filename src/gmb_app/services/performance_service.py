from data_fetcher import get_daily_metrics, get_posts, get_reviews, get_search_keywords


def fetch_dashboard_data(credentials, location_id, account_id, start_date, end_date):
    metrics_df = get_daily_metrics(credentials, location_id, start_date, end_date)
    keywords_df = get_search_keywords(credentials, location_id, start_date, end_date)
    reviews = get_reviews(credentials, location_id, account_id)
    posts = get_posts(credentials, location_id, account_id)
    return {
        "metrics_df": metrics_df,
        "keywords_df": keywords_df,
        "reviews": reviews,
        "posts": posts,
    }
