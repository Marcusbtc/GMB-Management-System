import google.generativeai as genai
import streamlit as st

def configure_ai(api_key):
    """Configures the Gemini API with the provided key."""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error configuring AI: {e}")
        return False

def generate_review_reply(review_text, rating, reviewer_name="Customer"):
    """Generates a reply to a customer review using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        You are a professional and polite business owner. 
        Write a response to the following Google Business Profile review.
        
        Reviewer: {reviewer_name}
        Rating: {rating} stars
        Review Text: "{review_text}"
        
        Guidelines:
        - Be professional, empathetic, and concise.
        - If the review is positive, thank them warmly.
        - If the review is negative, apologize for their experience and offer to make it right (ask them to contact us).
        - Do not include placeholders like [Your Name] or [Business Name], sign off as "The Management Team".
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating reply: {e}"
