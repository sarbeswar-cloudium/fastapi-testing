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
    page_assumes = ["","contact", "contact-us", "contactus", "get-in-touch", "support", "help"]

    data = []

    for site in sites.urls:
        for page in page_assumes:
            url = f"{site}/{page}"
            is_exist = url_exists_get(url)
            # skip, if url does not exist
            if is_exist is False: continue
            # find the contacts
            result = await scarpe(url)
            # making string
            emails = result['emails']
            phones = result['phones']
            emailStr = ", ".join(emails)
            phoneStr = ", ".join(phones)
            # new contact
            new_contact = models.ScrapedContacts(
                url = url,
                emails = emailStr,
                phones = phoneStr
            )
            db.add(new_contact)
            db.commit()
            db.refresh(new_contact)
            # data.append({
            #     "url": url,
            #     "emails": result["emails"],
            #     "phones": result["phones"]
            # })

    return {"message": "Successful!", "status": 1, "data": data}
            

def url_exists_get(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

async def scarpe(url: str):
    # Step 1: Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()

    # Step 2: Extract emails using regex
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

    # Step 3: Extract phone numbers (basic pattern)
    phones = re.findall(r'\+?\d[\d\s().-]{7,}\d', text)

    if emails == []:
        # emails = await scrape_email(url)
        emails = await scrape_email(url)
    
    # making unique
    emails = list(set(emails))
    phones = list(set(phones))

    return {"emails": emails, "phones": phones}


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
def download_csv(db: Session = Depends(get_db)):

    # Create an in-memory text stream
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["Url", "Emails", "Phones", "Created At"])

    # Write CSV headers and rows
    contacts = db.query(models.ScrapedContacts).all()

    for contact in contacts:
        writer.writerow([contact.url, contact.emails, contact.phones])

    
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