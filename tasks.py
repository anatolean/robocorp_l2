from robocorp.tasks import task
from robocorp import browser
import os

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    browser.configure(
        slowmo=500,
    )

    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        order_number = make_order(order)
        pdf_path = store_receipt_as_pdf(order_number)
        screenshot_path = screenshot_robot(order_number)
        embed_screenshot_to_receipt(screenshot_path, pdf_path)

        close_order_page()
        break
    archive_receipts()
    clean_up()


def open_robot_order_website():
    """Open a web site"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    """Close a modal window"""
    close_modal()

def get_orders():
    """Save csv from url"""
    http = HTTP()
    url = "https://robotsparebinindustries.com/orders.csv"
    target_file = "output/orders.csv"
    http.download(url, target_file, overwrite=True)

    """Convert csv to table"""
    tables = Tables()
    orders = tables.read_table_from_csv(
        target_file,
    )
    return orders

def close_modal():
    page = browser.page()
    try:
        page.locator(".btn-dark").click()
    except Exception as e:
        print("INFO-No modal in this case")

def make_order(order):   
    return fill_the_form(order)

def fill_the_form(order):
    page = browser.page()

    head_part = order['Head']
    page.locator("#head").select_option(head_part)

    body_part = order['Body']
    page.locator(f"#id-body-{body_part}").click()

    legs_part = order['Legs']
    page.locator("xpath=//div[3]/input").fill(legs_part)

    address_part = order['Address']
    page.locator("#address").fill("New York")

    page.locator("#preview").click()
    page.locator("#robot-preview > p").wait_for(timeout=10000)

    success = False
    while not success:
        page.locator("#order").click()
        try:
            page.locator("xpath=//h3[contains(.,'Receipt')]").wait_for(timeout=3000)
            success = True
        except Exception as e:
            print("WARN - Server failed. Repeat once again.")

    order_number = page.locator(".badge").text_content()
    return order_number

def store_receipt_as_pdf(order_number):
    pdf = PDF()
    page = browser.page()
    html_content = page.locator("#receipt").inner_html()
    output_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(
        content=html_content,
        output_path=output_path,  # Specify the output file path
        margin=0  # Optional: Set margins for the PDF
    )
    return output_path

def close_order_page():
    page = browser.page()
    page.locator("#order-another").click()
    close_modal()

def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = f"output/receipts/{order_number}.png"
    page.screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[screenshot_path],
        target_document=pdf_path,
        append=True
    )
    delete_file(screenshot_path)



def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", 'output/receipts.zip')

def clean_up():
    delete_directory("output/receipts")







"""Move to RobS library"""
def delete_file(file_path):
    try:
        os.remove(file_path)
        print("File deleted successfully.")
    except FileNotFoundError:
        print("The file does not exist.")

def delete_directory(directory_path):
    try:
        os.rmdir('path/to/directory')
        print("Directory deleted successfully.")
    except FileNotFoundError:
        print("Directory not found.")
    except OSError:
        print("Directory is not empty.")

"""Move to Robs library"""        