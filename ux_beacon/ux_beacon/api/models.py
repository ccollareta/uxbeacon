from django.db import models
from django.utils.timezone import now
import json
import os
import pdfkit

class WCAGReport(models.Model):
    """Model to store WCAG compliance results per website and user."""
    
    user_id = models.CharField(max_length=20)
    website_url = models.URLField()
    readability_score = models.CharField(max_length=50, blank=True, null=True)
    missing_alt_text = models.IntegerField(default=0)
    heading_structure = models.JSONField(default=dict)
    contrast_issues = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_report_path = models.CharField(max_length=255, blank=True, null=True)

    def run_wcag_check(self):
        """Runs WCAG compliance check and updates model instance."""
        from .wcag_checker import get_website_content, check_color_contrast, nlp_model
        from bs4 import BeautifulSoup
        
        html_content = get_website_content(self.website_url, self.user_id)
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Readability Check
            self.readability_score = nlp_model(" ".join([p.text for p in soup.find_all("p")])[:512])
            
            # Alt Text Check
            images = soup.find_all("img")
            self.missing_alt_text = len([img for img in images if not img.has_attr("alt") or img["alt"].strip() == ""])
            
            # Heading Structure
            self.heading_structure = {tag: len(soup.find_all(tag)) for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]}
            
            # Contrast Issues
            img_urls = [img["src"] for img in images if img.has_attr("src")]
            contrast_results = []
            for img_url in img_urls:
                contrast_results.append(check_color_contrast(img_url, self.user_id))
            self.contrast_issues = contrast_results
            
            # Save results
            self.save()
            print(f"WCAG check completed for {self.website_url} (User: {self.user_id})")

    def generate_wcag_report(self):
        """Generates a PDF report and stores the file path in the model."""
        pdf_folder = "media/reports"
        os.makedirs(pdf_folder, exist_ok=True)

        pdf_filename = f"wcag_report_{self.user_id}.pdf"
        pdf_path = os.path.join(pdf_folder, pdf_filename)

        html_report = f"""
        <html>
        <head><title>WCAG Compliance Report</title></head>
        <body>
            <h1>WCAG 2.0 Compliance Report</h1>
            <h2>Website: {self.website_url}</h2>
            <p><strong>Generated On:</strong> {self.created_at}</p>
            
            <h3>Readability Score</h3>
            <p>{self.readability_score}</p>

            <h3>Missing Alt Text</h3>
            <p>{self.missing_alt_text} images missing alt text</p>

            <h3>Heading Structure</h3>
            <p>{json.dumps(self.heading_structure, indent=2)}</p>

            <h3>Contrast Issues</h3>
            <p>{json.dumps(self.contrast_issues, indent=2)}</p>
        </body>
        </html>
        """

        with open(f"{pdf_folder}/wcag_report_{self.user_id}.html", "w") as file:
            file.write(html_report)

        pdfkit.from_file(f"{pdf_folder}/wcag_report_{self.user_id}.html", pdf_path)
        
        self.pdf_report_path = pdf_path
        self.save()

        print(f"WCAG Report generated: {pdf_path}")
        return pdf_path

    def __str__(self):
        return f"WCAG Report for {self.website_url} (User: {self.user_id})"
