from datetime import datetime, timedelta

import plotly.express as px
import streamlit as st

import ai_helper
import auth
import data_fetcher
import health_check
import report_generator
import visualizations
from src.gmb_app.core.config import get_gemini_api_key
from src.gmb_app.core.i18n import LANGUAGE_OPTIONS, translate
from src.gmb_app.services.performance_service import fetch_dashboard_data
from src.gmb_app.ui.create_post import render_create_post_tab

# Page Config
st.set_page_config(page_title="Google My Business Manager", layout="wide")

def t(key):
    lang = st.session_state.get("app_lang", "en")
    return translate(lang, key)


def get_default_ai_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", get_gemini_api_key())
    except Exception:
        return get_gemini_api_key()


def render_sidebar_config():
    if "app_lang" not in st.session_state:
        st.session_state["app_lang"] = "en"

    selected_label = next(
        (label for label, code in LANGUAGE_OPTIONS.items() if code == st.session_state["app_lang"]),
        "English",
    )
    new_label = st.sidebar.selectbox(
        t("language"),
        options=list(LANGUAGE_OPTIONS.keys()),
        index=list(LANGUAGE_OPTIONS.keys()).index(selected_label),
    )
    st.session_state["app_lang"] = LANGUAGE_OPTIONS[new_label]

    st.sidebar.header(t("configuration"))
    with st.sidebar.expander(t("ai_settings")):
        ai_api_key = st.text_input(t("gemini_key"), value=get_default_ai_key(), type="password")
        if ai_api_key:
            ai_helper.configure_ai(ai_api_key)


def resolve_selected_location(credentials):
    selected_location_obj = None
    selected_account_id = None
    location_id = "location_id_placeholder"

    if not credentials:
        return location_id, selected_location_obj, selected_account_id

    st.sidebar.success("Authenticated with Google")
    all_locations = data_fetcher.get_locations(credentials, account_name=None)
    if not all_locations:
        st.sidebar.warning("No locations found. Make sure you have access to at least one Google Business Profile.")
        return location_id, selected_location_obj, selected_account_id

    location_options = {loc["title"]: loc["name"] for loc in all_locations}
    selected_location_name = st.sidebar.selectbox("Select Business", list(location_options.keys()))
    location_id = location_options[selected_location_name]

    for loc in all_locations:
        if loc["name"] == location_id:
            selected_location_obj = loc
            if loc["name"].startswith("accounts/"):
                selected_account_id = "/".join(loc["name"].split("/")[:2])
            break

    with st.sidebar.expander("Location & Account IDs"):
        st.text_input(
            "Location ID",
            value=location_id,
            type="password",
            disabled=True,
        )
        st.text_input(
            "Account ID",
            value=selected_account_id or "Not resolved",
            type="password",
            disabled=True,
        )

    return location_id, selected_location_obj, selected_account_id


def fetch_data_if_requested(credentials, location_id, selected_account_id, start_date, end_date):
    if not st.sidebar.button(t("fetch_data")):
        return

    with st.spinner("Fetching data..."):
        dashboard_data = fetch_dashboard_data(
            credentials,
            location_id,
            selected_account_id,
            start_date,
            end_date,
        )
        st.session_state["metrics_df"] = dashboard_data["metrics_df"]
        st.session_state["keywords_df"] = dashboard_data["keywords_df"]
        st.session_state["reviews"] = dashboard_data["reviews"]
        st.session_state["posts"] = dashboard_data["posts"]
        st.session_state["data_fetched"] = True


def render_tab_overview(start_date, end_date):
    st.header("Performance Overview")
    if not st.session_state.get("data_fetched"):
        st.info("Click 'Fetch Data' in the sidebar to view the report.")
        return

    metrics_df = st.session_state["metrics_df"]
    keywords_df = st.session_state["keywords_df"]

    st.subheader("Daily Trends")
    if not metrics_df.empty:
        trend_df = metrics_df.copy()
        trend_df["Total Views"] = (
            trend_df.get("BUSINESS_IMPRESSIONS_DESKTOP_MAPS", 0)
            + trend_df.get("BUSINESS_IMPRESSIONS_DESKTOP_SEARCH", 0)
            + trend_df.get("BUSINESS_IMPRESSIONS_MOBILE_MAPS", 0)
            + trend_df.get("BUSINESS_IMPRESSIONS_MOBILE_SEARCH", 0)
        )
        trend_df["Total Actions"] = (
            trend_df.get("WEBSITE_CLICKS", 0)
            + trend_df.get("CALL_CLICKS", 0)
            + trend_df.get("BUSINESS_DIRECTION_REQUESTS", 0)
            + trend_df.get("BUSINESS_CONVERSATIONS", 0)
            + trend_df.get("BUSINESS_BOOKINGS", 0)
        )

        all_metrics = [col for col in trend_df.columns if col != "date"]
        selected_metrics = st.multiselect(
            "Select Metrics to Display",
            options=all_metrics,
            default=["Total Views", "Total Actions"],
        )

        if selected_metrics:
            fig_time = px.line(
                trend_df,
                x="date",
                y=selected_metrics,
                title="Performance Over Time",
                labels={"value": "Count", "date": "Date", "variable": "Metric"},
                template="plotly_white",
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Select at least one metric to display.")
    else:
        st.info("No daily trend data available.")

    st.subheader("Performance Overview")
    visualizations.display_metrics_cards(metrics_df)

    st.subheader("Platform & Device Breakdown")
    fig_platform = visualizations.plot_platform_breakdown(metrics_df)
    if fig_platform:
        st.plotly_chart(fig_platform, use_container_width=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Top Keywords")
        fig_kw = visualizations.plot_top_keywords(keywords_df)
        if fig_kw:
            st.plotly_chart(fig_kw, use_container_width=True)

    with col2:
        st.subheader("All Keywords")
        if not keywords_df.empty:
            st.dataframe(
                keywords_df[["keyword", "display_count"]],
                hide_index=True,
                use_container_width=True,
                height=400,
            )
        else:
            st.info("No keywords found.")

    st.subheader("Export Report")
    if st.button("Generate PDF Report"):
        pdf_path = report_generator.generate_pdf(metrics_df, keywords_df, start_date, end_date)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name="gmb_report.pdf",
                mime="application/pdf",
            )


def render_tab_reviews():
    st.header("Reviews Analysis")
    if not st.session_state.get("data_fetched"):
        st.info("Click 'Fetch Data' in the sidebar to view reviews.")
        return

    reviews = st.session_state.get("reviews", [])
    if not reviews:
        st.info("No reviews found.")
        return

    total_reviews = len(reviews)
    replied_reviews = sum(1 for r in reviews if "reviewReply" in r)
    unanswered_reviews = total_reviews - replied_reviews
    reply_rate = (replied_reviews / total_reviews * 100) if total_reviews > 0 else 0

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total Reviews", total_reviews)
    with col_stat2:
        st.metric("Replied", replied_reviews)
    with col_stat3:
        st.metric("Unanswered", unanswered_reviews, delta=f"{reply_rate:.1f}% replied")

    st.divider()

    col_r1, col_r2 = st.columns([1, 2])
    with col_r1:
        st.subheader("Sentiment Analysis")
        fig_rev = visualizations.plot_review_sentiment(reviews)
        if fig_rev:
            st.plotly_chart(fig_rev, use_container_width=True)

    with col_r2:
        st.subheader("Recent Reviews")
        filter_option = st.selectbox(
            "Filter reviews:",
            ["All Reviews", "Only Unanswered", "Only Answered"],
            key="review_filter",
        )

        if filter_option == "Only Unanswered":
            filtered_reviews = [r for r in reviews if "reviewReply" not in r]
        elif filter_option == "Only Answered":
            filtered_reviews = [r for r in reviews if "reviewReply" in r]
        else:
            filtered_reviews = reviews

        st.caption(f"Showing {len(filtered_reviews[:10])} of {len(filtered_reviews)} reviews")

        for i, review in enumerate(filtered_reviews[:10]):
            star_rating = review.get("starRating", "Unknown")
            reviewer_name = review.get("reviewer", {}).get("displayName", "Anonymous")

            with st.expander(f"{reviewer_name} - {star_rating} ⭐"):
                st.markdown("**Review:**")
                st.write(review.get("comment", "No comment"))
                st.caption(f"📅 {review.get('createTime', 'Unknown date')}")

                review_reply = review.get("reviewReply")
                if review_reply:
                    st.markdown("---")
                    st.markdown("**Your Reply:**")
                    st.info(review_reply.get("comment", "No reply text"))
                    st.caption(f"📅 Replied: {review_reply.get('updateTime', 'Unknown date')}")
                else:
                    st.warning("⚠️ Not replied yet")

                if st.button(f"Generate AI Reply #{i}", key=f"reply_btn_{i}"):
                    with st.spinner("Generating reply..."):
                        reply = ai_helper.generate_review_reply(
                            review.get("comment", ""),
                            star_rating,
                            reviewer_name,
                        )
                        st.text_area("Suggested Reply:", value=reply, height=100, key=f"reply_area_{i}")


def render_tab_posts():
    st.header("Posts Analysis")
    if not st.session_state.get("data_fetched"):
        st.info("Click 'Fetch Data' in the sidebar to view posts.")
        return

    posts = st.session_state.get("posts", [])
    if not posts:
        st.info("No posts found.")
        return

    st.subheader("Post Performance")
    fig_posts = visualizations.plot_post_performance(posts)
    if fig_posts:
        st.plotly_chart(fig_posts, use_container_width=True)

    st.subheader("Recent Posts")
    for post in posts[:5]:
        with st.expander(f"Post: {post.get('summary', 'No Summary')[:50]}..."):
            st.write(post.get("summary", ""))
            st.caption(f"Type: {post.get('topicType')} | State: {post.get('state')}")
            if post.get("callToAction"):
                st.write(f"CTA: {post.get('callToAction').get('actionType')}")


def render_tab_health(credentials, selected_location_obj, location_id):
    st.header("Profile Health Check")
    if not selected_location_obj:
        st.info("Select a location in the sidebar to view health analysis.")
        return

    if not st.session_state.get("data_fetched"):
        st.info("Click 'Fetch Data' in the sidebar to view health analysis.")
        return

    with st.spinner("Analyzing profile health..."):
        media_items = data_fetcher.get_media(credentials, location_id)
        questions = data_fetcher.get_questions(credentials, location_id)
        reviews = st.session_state.get("reviews", [])
        posts = st.session_state.get("posts", [])
        results = health_check.analyze_profile_health(selected_location_obj, reviews, posts, media_items, questions)

    st.subheader(f"Análise de Saúde da {selected_location_obj.get('title', 'Empresa')}")
    weak = sum(1 for r in results if r["status"] == "Weak")
    reasonable = sum(1 for r in results if r["status"] == "Reasonable")
    good = sum(1 for r in results if r["status"] == "Good")

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Fraco", weak, delta_color="inverse")
    col_s2.metric("Razoável", reasonable, delta_color="off")
    col_s3.metric("Bom", good)

    st.markdown("---")
    for result in results:
        with st.container():
            col_icon, col_content = st.columns([1, 10])
            with col_icon:
                if result["status"] == "Good":
                    st.success("✔")
                elif result["status"] == "Reasonable":
                    st.warning("!")
                else:
                    st.error("X")

            with col_content:
                st.subheader(result["title"])
                st.write(result["description"])

                if result["value"]:
                    st.caption(f"Valor Atual: {result['value']}")

                if result["recommendation"]:
                    if result["status"] == "Good":
                        st.success(result["recommendation"])
                    elif result["status"] == "Reasonable":
                        st.warning(result["recommendation"])
                    else:
                        st.error(result["recommendation"])

                score = result["score"]
                st.progress(score / 100)
                c1, c2, c3 = st.columns(3)
                c1.caption("Fraco")
                c2.caption("Razoável")
                c3.caption("Bom")

            st.markdown("---")


def render_tab_create_post(credentials, location_id, selected_account_id):
    render_create_post_tab(credentials, location_id, selected_account_id, t)


def main():
    st.title("Google My Business Manager")
    render_sidebar_config()

    credentials = auth.authenticate()
    location_id, selected_location_obj, selected_account_id = resolve_selected_location(credentials)

    st.sidebar.subheader("Date Range")
    today = datetime.today()
    default_start = today - timedelta(days=30)
    start_date = st.sidebar.date_input("Start Date", default_start)
    end_date = st.sidebar.date_input("End Date", today)

    if start_date > end_date:
        st.error("Start date must be before end date.")
        return

    fetch_data_if_requested(credentials, location_id, selected_account_id, start_date, end_date)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [t("overview"), t("reviews"), t("posts"), t("health"), t("create_post")]
    )

    with tab1:
        render_tab_overview(start_date, end_date)
    with tab2:
        render_tab_reviews()
    with tab3:
        render_tab_posts()
    with tab4:
        render_tab_health(credentials, selected_location_obj, location_id)
    with tab5:
        render_tab_create_post(credentials, location_id, selected_account_id)


if __name__ == "__main__":
    main()
