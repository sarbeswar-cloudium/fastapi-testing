from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from typing import List
import requests
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
import re
import io
import csv
import tracemalloc

tracemalloc.start()


router = APIRouter(
    prefix="/scraper",
    tags=["Scraper"]
)


@router.get('/', response_model=List[schemas.ScraperOut])
def get_contacts(db: Session = Depends(get_db)):

    contacts = db.query(models.ScrapedContacts).all()

    return contacts



@router.post("/")
async def scrape_contacts(sites: schemas.SiteList, db: Session = Depends(get_db)):
    page_assumes = ["","contact", "contact-us", "contactus", "get-in-touch", "support", "help", "contact-8"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://google.com",
        "Accept": "text/html"
    }

    data = []
    records = []

    for site in sites.urls:
        emails = []
        phones = []
        urls = []
        social_links = []
        for page in page_assumes:
            url = f"{site}/{page}"
            is_exist = await url_exists_get(url, headers)
            # skip, if url does not exist
            if is_exist is False: continue
            urls.append(url)
            # find the contacts
            result = await scarpe(url, headers)
            # collect all data
            emails.extend(result['emails'])
            phones.extend(result['phones'])
            social_links.extend(result['social_links'])

        # making unique
        emails = list(set(emails))
        phones = list(set(phones))
        social_links = list(set(social_links))
        # making string
        urlStr = ", ".join(urls)
        emailStr = ", ".join(emails)
        phoneStr = ", ".join(phones)
        sociallinkStr = ", ".join(social_links)

        # new contact
        # new_contact = models.ScrapedContacts(
        #     site = site,
        #     urls = urlStr,
        #     emails = emailStr,
        #     phones = phoneStr,
        #     social_links = sociallinkStr
        # )
        # db.add(new_contact)
        # db.commit()
        # db.refresh(new_contact)

        # records.append(new_contact.id)

        data.append({
            "site": site,
            "urls": urls,
            "emails": emails,
            "phones": phones,
            "social_links": social_links
        })

    return {"message": "Successful!", "status": 1, "data": data, "records": records}
            

async def url_exists_get(url, headers):
    try:
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

async def scarpe(url: str, headers):
    social_domains = [
        'facebook.com', 'twitter.com', 'linkedin.com',
        'instagram.com', 'youtube.com', 't.me'
    ]
    # Step 1: Fetch the webpage
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator=' ', strip=True)

    # pattern = r'''
    #     [a-zA-Z0-9._%+-]+       # username
    #     \s*(?:@|\[at\]|\(at\)|\{at\})\s*   # obfuscated @
    #     [a-zA-Z0-9.-]+\.[a-zA-Z]{2,}      # domain
    # '''

    pattern = r'''
        [a-zA-Z0-9._%+-]+                          # username
        (?:\s*(?:\[dot\]|\(dot\)|\{dot\})\s*[a-zA-Z0-9._%+-]+)*  # handle dot in username
        \s*(?:@|\[at\]|\(at\)|\{at\})\s*   # at symbol variants
        [a-zA-Z0-9-]+
        (?:\s*(?:\.|\[dot\]|\(dot\)|\{dot\})\s*[a-zA-Z]{2,})  # trailing space
    '''
    # Step 2: Extract emails using regex
    # emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    emails = re.findall(pattern, text, re.VERBOSE)

    # Step 3: Extract phone numbers (basic pattern)
    phones = re.findall(r'\+?\d[\d\s().-]{7,}\d', text)

    if emails == []:
        emails = await scrape_email(url)

    
    # making unique
    emails = list(set(emails))
    phones = list(set(phones))

    # update emails to correct format
    def normalize_obfuscated_email(email):
        email = re.sub(r'\s*(\[at\]|\(at\)|\{at\}|\s+at\s+)\s*', '@', email, flags=re.IGNORECASE)
        email = re.sub(r'\s*(\[dot\]|\(dot\)|\{dot\}|\s+dot\s+)\s*', '.', email, flags=re.IGNORECASE)
        email = re.sub(r'\?.*$', '', email, flags=re.IGNORECASE)
        return email

    emails = [normalize_obfuscated_email(email) for email in emails]

    # social media links
    try:
        links = soup.find_all('a', href=True)
        
        social_links = []
        for link in links:
            href = link['href']
            if any(domain in href for domain in social_domains):
                social_links.append(href)
        
        social_links = list(set(social_links))  # remove duplicates
    except Exception as e:
        return [f"Error: {e}"]

    return {"emails": emails, "phones": phones, "social_links": social_links}


# find emails only
async def scrape_email(url: str):
    emails = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_load_state('networkidle')

        # Get all mailto links
        elements = await page.query_selector_all("a[href^='mailto:']")
        

        for element in elements:
            href = await element.get_attribute('href')
            if href and href.startswith("mailto:"):
                emails.append(href.replace("mailto:", ""))

        await browser.close()

    return emails

# download csv data
@router.get("/download")
def download_csv(records: list = None, db: Session = Depends(get_db)):
    # Create an in-memory text stream
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Web Site", "Contact Url", "Email Address", "Phone Number", "Social Links", "Created At"])

    # Write CSV headers and rows
    contacts = db.query(models.ScrapedContacts)
    if records is not None:
        contacts = contacts.filter(models.ScrapedContacts.id in records).all()
    else:
        contacts = contacts.all()

    for contact in contacts:
        writer.writerow([contact.site, contact.urls, contact.emails, contact.phones, contact.social_links, contact.created_at])

    
    # Reset the stream position to the beginning
    output.seek(0)

    # Return a streaming response with correct headers
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=people.csv"
        }
    )
    