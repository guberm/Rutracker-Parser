import requests
from bs4 import BeautifulSoup

def parse_rutracker_forum(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table', {'class': 'vf-table vf-tor forumline forum'})
    if not table:
        print("Failed to find the table.")
        return []

    tbody = table.find('tbody')
    rows = tbody.find_all('tr', {'class': 'hl-tr'}) if tbody else table.find_all('tr', {'class': 'hl-tr'})

    torrents = []

    for row in rows:
        title_tag = row.find('td', {'class': 'vf-col-t-title'}).find('a', {'class': 'torTopic'})
        link = title_tag['href']
        post_link = f"https://rutracker.org/forum/{link}"
        post_response = requests.get(post_link)
        if post_response.status_code != 200:
            print(f"Failed to retrieve the post page. Status code: {post_response.status_code}")
            continue

        post_soup = BeautifulSoup(post_response.content, 'html.parser')
        title = post_soup.find('title').text
        image_tag = post_soup.find('var', {'class': 'postImg postImgAligned img-right'})
        image_url = image_tag['title'] if image_tag else None

        description_span = post_soup.find('span', {'class': 'post-b'}, string='Описание')
        description = None
        if description_span:
            next_sibling = description_span.next_sibling
            description_parts = []
            while next_sibling and (next_sibling.name != 'hr'):
                if isinstance(next_sibling, str):
                    description_parts.append(next_sibling.strip())
                next_sibling = next_sibling.next_sibling
            description = ' '.join(description_parts).strip() if description_parts else None
            if description and description.startswith(':'):
                description = description[1:].strip()
        
        magnet_link_tag = post_soup.find('a', {'class': 'magnet-link'})
        magnet_link = magnet_link_tag['href'] if magnet_link_tag else None

        torrents.append({
            'title': title,
            'url': post_link,
            'image_url': image_url,
            'description': description,
            'magnet_link': magnet_link
        })

    return torrents

forum_url = 'https://rutracker.org/forum/viewforum.php?f=252'
parsed_data = parse_rutracker_forum(forum_url)

for torrent in parsed_data:
    print(f"Title: {torrent['title']}")    
    print(f"Url: {torrent['url']}")
    print(f"Image URL: {torrent['image_url']}")
    print(f"Description: {torrent['description']}")
    print(f"Magnet Link: {torrent['magnet_link']}\n")
    print('-' * 40)
