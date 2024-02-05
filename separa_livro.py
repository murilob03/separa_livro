import re, argparse, os

import PyPDF2


def get_bookmarks(pdf_reader, outlines, bookmarks, depth=0):
    """
    Extracts bookmarks from the PDF and adds them to the 'bookmarks' list, considering the specified depth.

    Parameters:
    - pdf_reader: PyPDF2.PdfReader object for the PDF.
    - outlines: List of bookmark outlines from the PDF.
    - bookmarks: List to store bookmarks in the form of (title, page number).
    - depth: Integer specifying the depth of bookmarks to extract, with -1 for all levels.
    """
    for outline in outlines:
        if isinstance(outline, list):
            # Recursively print bookmarks from sublists
            if depth > 0:
                get_bookmarks(pdf_reader, outline, bookmarks, depth - 1)
            elif depth == -1:
                get_bookmarks(pdf_reader, outline, bookmarks, depth)
        else:
            if depth < 1:
                bookmarks.append(
                    (outline.title, pdf_reader.get_destination_page_number(outline))
                )


def print_bookmarks(bookmarks):
    """
    Prints the list of bookmarks to the console.

    Parameters:
    - bookmarks: List of bookmarks (title, page number) to be printed.
    """
    for title, page in bookmarks:
        print(f"{title} - {page}")


def separate_by_bookmark(pdf_reader, bookmarks, key="", output_path="", mock=False):
    """
    Creates individual PDF files for each bookmark section, or mocks the process if specified.

    Parameters:
    - pdf_reader: PyPDF2.PdfReader object for the PDF.
    - bookmarks: List of bookmarks to base the separation on.
    - key: String keyword to filter bookmarks by title.
    - output_path: String path to save the separated PDFs.
    - mock: Boolean indicating whether to run in mock mode, printing info instead of creating files.
    """
    # Get the end page for each bookmark
    for i, (title, start_page) in enumerate(bookmarks):
        end_page = (
            bookmarks[i + 1][1] if i + 1 < len(bookmarks) else len(pdf_reader.pages)
        )

        # Create a PdfWriter object for the output PDF
        pdf_writer = PyPDF2.PdfWriter()

        if not key or key in title:  # Filter bookmarks by keyword
            if mock:  # Print info instead of creating files
                print(f"Title: {title}")
                print(f"Start page: {start_page}")
                print(f"End page: {end_page}")
                print()
            else:
                for page_num in range(
                    start_page, end_page
                ):  # Add pages to the output PDF
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                output_filename = f"{title.replace(' ', '_')}.pdf"
                output_filename = sanitize_file_name(output_filename)
                if output_path:
                    output_filename = os.path.join(output_path, output_filename)

                with open(output_filename, "wb") as output_pdf:
                    pdf_writer.write(output_pdf)
                print(f"Created: {output_filename}")


def sanitize_file_name(input_string, replacement="_", max_length=None):
    """
    Sanitizes a string for safe use as a file name by replacing invalid characters and optionally truncating.

    Parameters:
    - input_string: The original file name string.
    - replacement: Character used to replace invalid characters.
    - max_length: Optional maximum length for the sanitized string.

    Returns:
    - The sanitized file name as a string.
    """
    # Define a regex pattern to match invalid characters
    invalid_chars = r'[\\/:*?"<>|]'

    # Replace invalid characters with the specified replacement
    sanitized_string = re.sub(invalid_chars, replacement, input_string)

    # Replace spaces with underscores
    sanitized_string = sanitized_string.replace(" ", replacement)

    # Optionally limit the length of the file name
    if max_length is not None and len(sanitized_string) > max_length:
        sanitized_string = sanitized_string[:max_length]

    return sanitized_string


parser = argparse.ArgumentParser(description="Separate PDF by bookmarks")

parser.add_argument("-m", "--mock", action="store_true", help="mock run")
parser.add_argument(
    "-d", "--depth", type=int, default=-1, help="depth of the bookmarks"
)
parser.add_argument("-k", "--key", type=str, default="", help="key to filter bookmarks")
parser.add_argument("-o", "--output", type=str, default="", help="output path")
parser.add_argument(
    "pdf_path", metavar="pdf_path", type=str, help="path to the pdf file"
)

args = parser.parse_args()


def main():
    if not os.path.isfile(args.pdf_path):  # Check if the PDF file exists
        print("Invalid PDF path")
        return

    if not os.path.isdir(args.output) and args.output:
        try:
            os.makedirs(args.output)
        except OSError:
            print("Invalid output path")
            return

    pdf_reader = PyPDF2.PdfReader(args.pdf_path)
    outlines = pdf_reader.outline
    bookmarks = []

    get_bookmarks(pdf_reader, outlines, bookmarks, args.depth)
    separate_by_bookmark(pdf_reader, bookmarks, args.key, args.output, args.mock)


if __name__ == "__main__":
    main()
