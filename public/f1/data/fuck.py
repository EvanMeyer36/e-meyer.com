import re
from bs4 import BeautifulSoup
import os

def create_xhtml_files(input_file_path, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    chapter_splits = re.split(r'Chapter (\d+): ([^\n]+)\n', content)[1:]

    for i in range(0, len(chapter_splits), 3):
        chapter_number = chapter_splits[i]
        chapter_title = chapter_splits[i + 1]
        chapter_content = chapter_splits[i + 2]

        soup = BeautifulSoup('', 'html.parser')
        h1_tag = soup.new_tag('h1')
        h1_tag.string = f"Chapter {chapter_number}: {chapter_title}"
        soup.append(h1_tag)

        for paragraph in chapter_content.strip().split('\n\n'):
            p_tag = soup.new_tag('p')
            p_tag.string = paragraph.strip()
            soup.append(p_tag)

        xhtml_content = soup.prettify(formatter="html")
        output_file_path = os.path.join(output_directory, f"chapter_{chapter_number}.xhtml")

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(xhtml_content)

        print(f"Chapter {chapter_number} saved to {output_file_path}")

# Example usage
input_file_path = 'I:/swagradio/res/swag2.txt'  # Replace with the path to your text file
output_directory = 'I:/swagradio/res'   # Replace with your desired output directory
create_xhtml_files(input_file_path, output_directory)
