import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from transformers import pipeline

# Load Pre-trained Models
image_model = models.resnet18(pretrained=True)
image_model.eval()

nlp_model = pipeline("text-classification", model="bert-base-uncased")

# Image Preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def check_color_contrast(image_url, user_id):
    """Uses OpenCV to check color contrast in images (WCAG AA)."""
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        img_cv = np.array(image)

        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
        
        # Calculate contrast (Luminance ratio)
        min_lum = np.min(gray)
        max_lum = np.max(gray)
        contrast_ratio = (max_lum + 0.05) / (min_lum + 0.05)

        # WCAG 2.0 contrast ratio requirement (AA standard: 4.5:1)
        is_compliant = contrast_ratio >= 4.5
        print(f"[{user_id}] Image Contrast Ratio: {contrast_ratio:.2f} (Compliant: {is_compliant})")

    except Exception as e:
        print(f"[{user_id}] Error analyzing contrast: {e}")

def analyze_html_nlp(html_content, user_id):
    """Uses NLP to check for missing alt text, poor heading structures, and other issues."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Check for missing alt text in images
    images = soup.find_all("img")
    missing_alt = [img for img in images if not img.has_attr("alt") or img["alt"].strip() == ""]

    # Extract text for NLP analysis
    text_content = " ".join([p.text for p in soup.find_all("p")])

    # Classify the text for readability issues
    readability_result = nlp_model(text_content[:512])  # Limit to 512 tokens
    print(f"[{user_id}] Readability Analysis: {readability_result}")

    # Heading structure
    headings = {tag: len(soup.find_all(tag)) for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]}
    
    print(f"[{user_id}] Images without alt text: {len(missing_alt)}")
    print(f"[{user_id}] Heading Structure: {headings}")

def get_website_content(url, user_id):
    """Fetches the webpage content using Selenium."""
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        driver.quit()
        print(f"[{user_id}] Error fetching website: {e}")
        return None

def run_wcag_check(url, user_id):
    """Triggers ADA compliance check for a given URL and user ID."""
    print(f"[{user_id}] Running ADA WCAG 2.0 Compliance Check for: {url}")

    html_content = get_website_content(url, user_id)

    if html_content:
        analyze_html_nlp(html_content, user_id)
        
        # Analyze images
        soup = BeautifulSoup(html_content, "html.parser")
        img_urls = [img["src"] for img in soup.find_all("img") if img.has_attr("src")]
        
        for img_url in img_urls:
            check_color_contrast(img_url, user_id)


