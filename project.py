from fpdf import FPDF
from fpdf.enums import XPos, YPos
from bs4 import BeautifulSoup
import requests
import re
import logging


def main():
    while True:
        if search_response:= search_requester(get_novel_title()):
            if search_results:= get_search_results(search_response):
                if picked_novel:= novel_picker(search_results):
                    break
    picked_chapters = chapters_picker(picked_novel)
    download_chapters_to_pdf(picked_chapters, picked_novel["title"], picked_novel["link"])


def get_novel_title(): 
    while True:
        if novel_title:= input("Novel's title: ").strip().lower():
            return novel_title
        else:
            print("The title field cannot be empty please try again.")


def search_requester(novel_title):
    url = f"https://allnovelfull.net/search?keyword={novel_title}"
    for _ in range(3):
        try:
            search_response = requests.get(url)
            search_response.raise_for_status()
            return search_response.content
        except requests.exceptions.HTTPError as errh:
            logging.warning(f"HTTP Error {errh}")
            break
        except requests.exceptions.ConnectionError as errc:
            logging.warning(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            logging.warning(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            logging.warning(f"Unexpected Error: {err}")
    logging.warning(f"Failed to retrieve {url} after 3 attempts Please try again later or check the spelling of the novel title and try again.")
    return None
    
    
def get_search_results(search_response):
    search_results = []
    soup = BeautifulSoup(search_response, "lxml")
    if novels:= soup.find("div", {"class": "list list-truyen col-xs-12"}).find_all("div", {"class": "row"}):
        for novel in novels:
            search_results.append(
                {
                    "title": novel.find("h3", {"class": "truyen-title"}).a.text.strip(),
                    "link": novel.find("h3", {"class": "truyen-title"}).a["href"],
                    "chapters": novel.find("span", {"chapter-text"}).text.strip(),
                }
            )
        return search_results
    else:
        print("Novel not found, Either a typo or the novel isn't currently available. Try again")


def novel_picker(search_results):
    for i, result in enumerate(search_results):
        print(f"{i+1}. {result['title']}  [{result['chapters']}]")
    print("00. The novel isn't in the list. Go back")
    while True:
        try:
            user_choice = int(input("Your pick: ").strip())
            if user_choice == 0:
                break
            else:
                return search_results[user_choice-1]
        except ValueError:
            print("Invalid input. Please type the index(number) of the novel")
        except IndexError:
            print("Invalid input. The number you've typed isn't in the displayed list")


def chapters_picker(picked_novel):
    chapters_count = re.search(r"Chapter (\d+)", picked_novel["chapters"], re.IGNORECASE)
    print(f"Novel: {picked_novel['title']}\nChapters: {chapters_count.group(1)} chapters available")
    while True:
        try:
            starting_index, ending_index = int(input("Download from: ")), int(input("to: "))
            if 0 < starting_index <= ending_index <= int(chapters_count.group(1)):
                return range(starting_index, ending_index+1)
            elif ending_index < starting_index:
                print("the ending index must be equal or bigger than the starting index")
                continue
            else:
                raise IndexError
        except ValueError:
            print("The starting and ending indexes must be numbers")
        except IndexError:
            print(f"The starting and ending indexes must be in the range of the available chapters ({chapters_count.group(1)} chapters)")


def download_chapters_to_pdf(selected_chapters, novel_title, novel_link):
    pdf = generate_pdf()
    for i in selected_chapters:
        if chapter_content:= get_chapter_content(novel_link, i):
            chapter_text = extract_text(chapter_content)
            write_chapter_to_pdf(pdf, chapter_text)
            print(f"chapter {i} downloaded successfully!")
    print("Task completed!")
    pdf.output(f"{novel_title}.pdf")
    

def get_chapter_content(novel_link, current_chapter):
    url = f"https://allnovelfull.net{novel_link.replace('.html', '')}/chapter-{current_chapter}.html"
    for _ in range(3):
        try:
            chapter = requests.get(url)
            chapter.raise_for_status()
            return chapter.content
        except requests.exceptions.HTTPError as errh:
            logging.warning(f"HTTP Error {errh}")
            break
        except requests.exceptions.ConnectionError as errc:
            logging.warning(f"Connection Error {errc}")
        except requests.exceptions.Timeout as errt:
            logging.warning(f"Timeout Error {errt}")
        except requests.exceptions.RequestException as err:
            logging.warning(f"Unexpected Error {err}")
    logging.warning(f"Failed to retrieve {url} after 3 attempts, skipping chapter")
    return None


def extract_text(chapter_content):
    soup = BeautifulSoup(chapter_content, "lxml")
    full_chapter = [p.text.strip() for p in (soup.find("div", {"id":"chapter-content"}).find_all("p")) if p.text.strip() != ""]
    full_chapter.insert(0, soup.find("a", {"class":"chapter-title"})["title"])
    return full_chapter


def generate_pdf():
    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(top=20, right=20, left=20)
    pdf.add_font('Arial', '', r"arial.ttf")
    pdf.add_font('Arial', 'BI', r"arialbi.ttf")
    return pdf


def write_chapter_to_pdf(pdf, chapter_text):
    pdf.add_page()
    pdf.set_font("Arial", "BI", 16)
    pdf.cell(0, 15, chapter_text[0], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_font("Arial", "", 14)
    for paragraph in chapter_text[1:]:
        pdf.multi_cell(0, 9, paragraph, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(8)


if __name__ == "__main__":
    main()
