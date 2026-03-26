from mimesis import Text, Address
from playwright.sync_api import Page, expect
from ..conftest import BASE_URL

text = Text('en')
address = Address('en')

def test_create_journey_for_edit_log(page: Page):
    page.goto("https://comp639prj2rar.pythonanywhere.com/home")
    expect(page.get_by_role("link", name="Get Started")).to_be_visible()
    page.get_by_role("link", name="Get Started").click()
    # Login as free user
    page.get_by_role("textbox", name=" Username").click()
    page.get_by_role("textbox", name=" Username").fill("testuser1")
    page.get_by_role("textbox", name=" Password").click()
    page.get_by_role("textbox", name=" Password").fill("1qaz@WSX")
    page.get_by_role("button", name="Log In").click()
    # Create a journey for free user
    page.get_by_role("link", name=" My Journey").click()
    edit_link = page.get_by_role("link", name="First Journey")
    if edit_link.count() > 0:
        edit_link.click()
        page.get_by_role("button", name=" Delete Journey").click()
        page.get_by_role("button", name="Delete", exact=True).click()

    page.get_by_role("link", name=" Journey").click()
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill("First Journey")
    page.get_by_role("textbox", name=" Start Date *").fill("2025-06-10")
    page.get_by_role("textbox", name=" Description *").click()
    page.get_by_role("textbox", name=" Description *").fill("First Journey")
    page.get_by_label("Sharing *").select_option("public")
    page.get_by_role("button", name=" Add Journey").click()
    # Create a event for free user
    page.get_by_role("link", name=" My Journey").click()
    page.get_by_role("link", name="First Journey").click()
    page.get_by_role("link", name=" Add Event").click()
    page.get_by_role("textbox", name="Title *").click()
    page.get_by_role("textbox", name="Title *").fill("First Event")
    page.get_by_role("textbox", name="Start Date *").fill("2025-06-10")
    page.get_by_role("textbox", name="Start Time *").click()
    page.get_by_role("textbox", name="Start Time *").press("ArrowUp")
    page.get_by_role("textbox", name="Start Time *").press("ArrowRight")
    page.get_by_role("textbox", name="Start Time *").press("ArrowUp")
    page.get_by_role("textbox", name="Start Time *").press("ArrowRight")
    page.get_by_role("textbox", name="Start Time *").press("ArrowUp")
    page.locator("#location_id").select_option("7")
    page.get_by_role("button", name=" Add Event").click()
    
    page.pause()