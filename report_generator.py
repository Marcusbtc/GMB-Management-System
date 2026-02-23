from fpdf import FPDF
import tempfile

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Google My Business Manager Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(metrics_df, keywords_df, start_date, end_date):
    """Generates a PDF report with summary and tables."""
    pdf = PDFReport()
    pdf.add_page()
    
    # Title and Date Range
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Report Period: {start_date} to {end_date}", 0, 1, 'L')
    pdf.ln(5)
    
    # Summary Metrics
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Summary Metrics", 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    
    if not metrics_df.empty:
        # Calculate Totals
        total_views = (
            metrics_df.get('BUSINESS_IMPRESSIONS_DESKTOP_MAPS', 0).sum() +
            metrics_df.get('BUSINESS_IMPRESSIONS_DESKTOP_SEARCH', 0).sum() +
            metrics_df.get('BUSINESS_IMPRESSIONS_MOBILE_MAPS', 0).sum() +
            metrics_df.get('BUSINESS_IMPRESSIONS_MOBILE_SEARCH', 0).sum()
        )
        
        total_actions = (
            metrics_df.get('WEBSITE_CLICKS', 0).sum() +
            metrics_df.get('CALL_CLICKS', 0).sum() +
            metrics_df.get('BUSINESS_DIRECTION_REQUESTS', 0).sum() +
            metrics_df.get('BUSINESS_CONVERSATIONS', 0).sum() +
            metrics_df.get('BUSINESS_BOOKINGS', 0).sum()
        )
        
        pdf.cell(0, 10, f"Total Views: {int(total_views):,}", 0, 1)
        pdf.cell(0, 10, f"Total Interactions: {int(total_actions):,}", 0, 1)
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Interaction Details:", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"Website Clicks: {int(metrics_df.get('WEBSITE_CLICKS', 0).sum()):,}", 0, 1)
        pdf.cell(0, 8, f"Calls: {int(metrics_df.get('CALL_CLICKS', 0).sum()):,}", 0, 1)
        pdf.cell(0, 8, f"Directions: {int(metrics_df.get('BUSINESS_DIRECTION_REQUESTS', 0).sum()):,}", 0, 1)
        pdf.cell(0, 8, f"Messages: {int(metrics_df.get('BUSINESS_CONVERSATIONS', 0).sum()):,}", 0, 1)
        pdf.cell(0, 8, f"Bookings: {int(metrics_df.get('BUSINESS_BOOKINGS', 0).sum()):,}", 0, 1)

    else:
        pdf.cell(0, 10, "No metrics data available.", 0, 1)
        
    pdf.ln(10)
    
    # Top Keywords Table
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Top Search Keywords", 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    
    if not keywords_df.empty:
        # Table Header
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(100, 10, "Keyword", 1, 0, 'C', 1)
        pdf.cell(40, 10, "Count", 1, 1, 'C', 1)
        
        # Table Rows
        for index, row in keywords_df.head(10).iterrows():
            pdf.cell(100, 10, str(row['keyword']), 1, 0, 'L')
            pdf.cell(40, 10, str(row['display_count']), 1, 1, 'C')
    else:
        pdf.cell(0, 10, "No keyword data available.", 0, 1)

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name
