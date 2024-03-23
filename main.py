import httpx
from selectolax.parser import HTMLParser
import time
from dataclasses import dataclass, asdict, fields
import json
import csv


@dataclass
class Item:
    headline: str
    publish_date: str
    author: str


def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
    }
    resp = httpx.get(url, headers=headers)
    html = HTMLParser(resp.text)
    return html


def extract_text(html, sel):
    try:
        return html.css_first(sel).text(strip=True)
    except AttributeError:
        return None


def parse_page_urls(html):
    stories = html.css("div.story-wrap")
    for story in stories:
        url = story.css_first("div.story-text > a").attributes["href"]
        if url[0:19] != "https://www.npr.org":
            # Not a valid url
            continue
        else:
            yield url


def parse_article(html):

    article = Item(
        headline=extract_text(html, "div.storytitle h1"),
        publish_date=extract_text(html, "time > span.date"),
        author=extract_text(html, "p.byline__name"),
    )

    return asdict(article)


def extract_to_json(articles):
    with open('articles.json','w',encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=True, indent=4)
    print('Saved to JSON')


def extract_to_csv(articles):
    field_names = [field.name for field in fields(Item)]
    with open('articles.csv','w',encoding='utf-8') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()
        writer.writerows(articles)
    print('Saved to CSV')



def main():
    url = "https://www.npr.org"
    html = get_html(url)
    story_urls = parse_page_urls(html)
    articles = []
    for url in story_urls:
        html = get_html(url)
        print(url)
        articles.append(parse_article(html))
        time.sleep(0.5)
    extract_to_json(articles)
    extract_to_csv(articles)


if __name__ == "__main__":
    main()
