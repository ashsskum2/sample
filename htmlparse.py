#ashsskum2
import os
import glob
from bs4 import BeautifulSoup

# Function to read HTML content from a file
def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to write extracted text to a file
def write_text_to_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Extract text content
    text = soup.get_text(separator=' ', strip=True)

    # Extract hyperlinks
    links = [(a.get_text(strip=True), a['href']) for a in soup.find_all('a', href=True)]

    # Extract and denormalize table data
    tables = []
    for table in soup.find_all('table'):
        table_data = []
        rowspan_cells = {}

        for row_idx, row in enumerate(table.find_all('tr')):
            row_data = []
            cell_idx = 0

            while cell_idx < len(row.find_all(['th', 'td'])) or rowspan_cells.get((row_idx, cell_idx)):
                if rowspan_cells.get((row_idx, cell_idx)):
                    cell_text = rowspan_cells[(row_idx, cell_idx)]
                    row_data.append(cell_text)
                    cell_idx += 1
                else:
                    cell = row.find_all(['th', 'td'])[cell_idx]
                    cell_text = ' '.join(cell.stripped_strings)  # Convert multi-line text to single line
                    row_data.append(cell_text)

                    rowspan = int(cell.get('rowspan', 1))
                    colspan = int(cell.get('colspan', 1))

                    if rowspan > 1:
                        for i in range(1, rowspan):
                            rowspan_cells[(row_idx + i, cell_idx)] = cell_text

                    cell_idx += colspan

            table_data.append(row_data)
        tables.append(table_data)

    # Formatting output
    formatted_text = f"Extracted Text:\n{text}\n"
    formatted_text += "\nHyperlinks:\n"
    for text, url in links:
        formatted_text += f"{text}: {url}\n"
    formatted_text += "\nTables:\n"
    for table in tables:
        for row in table:
            formatted_row = ' | '.join(row)
            formatted_text += formatted_row + "\n"
        formatted_text += "\n"

    return formatted_text

def process_html_files_in_folder(folder_path):
    # Get all HTML files in the folder
    html_files = glob.glob(os.path.join(folder_path, "*.html"))

    for html_file in html_files:
        # Read HTML content
        html_content = read_html_file(html_file)

        # Extract text from HTML
        extracted_text = extract_text_from_html(html_content)

        # Write extracted text to new file with "_parsed" suffix
        base_name = os.path.basename(html_file)
        new_file_name = os.path.splitext(base_name)[0] + "_parsed.txt"
        new_file_path = os.path.join(folder_path, new_file_name)

        write_text_to_file(new_file_path, extracted_text)

# Usage
folder_path = 'path_to_your_folder'  # Replace with your folder path
process_html_files_in_folder(folder_path)
