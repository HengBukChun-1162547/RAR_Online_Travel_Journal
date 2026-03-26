import time
from mimesis import Person
from playwright.sync_api import Page, expect
from ..conftest import BASE_URL, APP_REGISTRATION_URL

test_data_tr1 = [];
test_data_tr2 = [];

def test_run(page: Page, fake_data: Person):
    
    # Test data - Traveller 1
    first_name = fake_data.first_name()
    test_data_tr1.append({"first_name" : first_name})
    
    last_name = fake_data.last_name()
    test_data_tr1.append({"last_name" : last_name})
    
    username = "traveller_"+first_name.lower()+"1"
    test_data_tr1.append({"username" : username})
    
    email = first_name+last_name+"@gmail.com"
    test_data_tr1.append({"email" : email})
    
    location = "Lincoln"
    password = "Test@123"
    
    # Journey
    journey_name = first_name+"s Journey"
    test_data_tr1.append({"journey_name" : journey_name})
    
    start_date = "2025-10-20"
    test_data_tr1.append({"start_date" : start_date})
    
    description = fake_data.worldview()
    test_data_tr1.append({"description" : description})
    
    #Event -1
    event_name1 = first_name+"s First Event"
    test_data_tr1.append({"event_name1" : event_name1})
    
    event_start_date1 = "2025-10-21"
    event_start_time1 = "14:30"
    
    #Event -1
    event_name2 = first_name+"s Second Event"
    test_data_tr1.append({"event_name2" : event_name2})
    
    event_start_date2 = "2025-11-21"
    event_start_time2 = "16:30"
    
    
    page.goto(BASE_URL)
    
    # Registration
    page.get_by_role("link", name="Register").click()
    page.get_by_role("textbox", name="Username *").fill(username)
    page.get_by_role("textbox", name="First Name").fill(first_name)
    page.get_by_role("textbox", name="Last Name").fill(last_name)
    page.get_by_role("textbox", name="Email *").fill(email)
    page.get_by_role("textbox", name="Location").fill(location)
    page.get_by_role("textbox", name=" Password *").fill(password)
    page.get_by_role("textbox", name=" Confirm Password *").fill(password)
    page.get_by_role("button", name="Sign Up").click()
    # validation
    expect(page.get_by_role("heading", name="Log in")).to_be_visible()
    
    # Login
    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Log In").click()
    # validation
    expect(page.locator(".card-body").first).to_be_visible()
    
    # Create new public journey
    page.get_by_role("link", name="View My Journeys").click()
    expect(page.locator("h4")).to_contain_text("My Journey")
    page.get_by_role("link", name=" Create Your First Journey").click()
    expect(page.get_by_role("heading", name="New Journey")).to_be_visible()
    page.get_by_role("textbox", name="Title *").fill(journey_name)
    page.fill('input[name="start_date"]', start_date)
    page.get_by_label("Sharing *").select_option("public")
    page.get_by_role("textbox", name="Description *").fill(description)
    page.get_by_role("button", name=" Add Journey").click()
    expect(page.get_by_text("Journey added successfully")).to_be_visible()
    
    #First Event
    page.get_by_role("link", name=journey_name).click()
    page.get_by_role("link", name=" Add Event").click()
    page.get_by_role("textbox", name="Title *").fill(event_name1)
    page.fill('input[name="start_date"]', event_start_date1)
    page.fill('input[name="start_time"]', event_start_time1)
    page.locator("#location_id").select_option(label="Australia")
    page.set_input_files("input[type='file']", "test/data/image/aus.jpeg")
    page.get_by_role("button", name=" Add Event").click()
    expect(page.get_by_text("Successfully added the new event")).to_be_visible()
    
    #Second Event
    page.get_by_role("link", name=" Add Event").click()
    page.get_by_role("textbox", name="Title *").fill(event_name2)
    page.fill('input[name="start_date"]', event_start_date2)
    page.fill('input[name="start_time"]', event_start_time2)
    page.locator("#location_id").select_option(label="Canada")
    page.set_input_files("input[type='file']", "test/data/image/aus.jpeg")
    page.get_by_role("button", name=" Add Event").click()
    expect(page.get_by_text("Successfully added the new event")).to_be_visible()
    
    page.get_by_role("link", name=" Home").click()
    page.get_by_role("link", name=" Premium Features").nth(1).click()
    page.get_by_role("link", name=" Departure Board").click()
    expect(page.locator("#premiumFeatureModalLabel")).to_contain_text("Unlock 'Departure Board' Features")
    page.get_by_role("button", name="Maybe Later").click()
    
    page.click('div[class="user-section p-3"] a[data-bs-toggle="dropdown"]')
    page.get_by_role("link", name=" Sign out").click()
    
    # -----------End of first traveller----------------
    
    print(test_data_tr1);
    
    
    
def test_traveller_2(page: Page, fake_data: Person):
    
    # Test data - Traveller 1
    first_name = fake_data.first_name()
    test_data_tr2.append({"first_name" : first_name})
    
    last_name = fake_data.last_name()
    test_data_tr2.append({"last_name" : last_name})
    
    username = "traveller_"+first_name.lower()+"1"
    test_data_tr2.append({"username" : username})
    
    email = first_name+last_name+"@gmail.com"
    test_data_tr2.append({"email" : email})
    
    location = "Lincoln"
    password = "Test@123"
    
    # Journey
    journey_name = first_name+"s Journey"
    test_data_tr2.append({"journey_name" : journey_name})
    
    page.goto(APP_REGISTRATION_URL);
    
    # Registration
    page.get_by_role("link", name="Register").click()
    page.get_by_role("textbox", name="Username *").fill(username)
    page.get_by_role("textbox", name="First Name").fill(first_name)
    page.get_by_role("textbox", name="Last Name").fill(last_name)
    page.get_by_role("textbox", name="Email *").fill(email)
    page.get_by_role("textbox", name="Location").fill(location)
    page.get_by_role("textbox", name=" Password *").fill(password)
    page.get_by_role("textbox", name=" Confirm Password *").fill(password)
    page.get_by_role("button", name="Sign Up").click()
    # validation
    expect(page.get_by_role("heading", name="Log in")).to_be_visible()
    
    # Login
    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Log In").click()
    # validation
    expect(page.locator(".card-body").first).to_be_visible()
    
    page.get_by_role("link", name="Manage Subscriptions").click()
    page.get_by_role("link", name="Top Up").click()
    
    def handle_dialog(dialog):
        print("Dialog message:", dialog.message)
        dialog.accept() 

    page.once("dialog", handle_dialog)  # Register before click
    page.click("(//form[@action='/premium_features/subscribe'])[1]")
    
    # time.sleep(3)
    
    page.get_by_role("textbox", name="-0000-0000-0000").fill("9876-9877-2234-3487")
    page.get_by_role("textbox", name="MM/YYYY").fill("01/2029")
    
    
    page.get_by_role("textbox", name="123").fill("989")
    page.locator("input[name=\"cardHolder\"]").fill(first_name+" "+last_name)
    page.locator("select[name=\"cardType\"]").select_option("Visa")
    page.locator("#country").select_option("NZ")
    page.locator("#addressLine1").fill("41 Raurimu Avenue")
    page.locator("#addressLine2").fill("Rolleston")
    page.locator("#city").fill("Wellington")
    page.locator("#state").fill("Selwyn")
    page.locator("#postalCode").fill("76787")
    page.get_by_role("checkbox", name="I have read and agree to the").check()
    
    page.once("dialog", handle_dialog)  # Register before click
    page.get_by_role("button", name="Confirm Payment").click()
    time.sleep(2)
    
    page.click('div[class="user-section p-3"] a[data-bs-toggle="dropdown"]')
    page.get_by_role("link", name=" Sign out").click()
    
    page.get_by_role("link", name="Login").click()
    page.get_by_role("textbox", name="Username").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Log In").click()
    # validation
    expect(page.locator(".card-body").first).to_be_visible()
    
    
    
    
    
    # page.get_by_role("link", name=" Home").click()
    # page.get_by_role("link", name=" Premium Features").nth(1).click()
    page.get_by_role("link", name=" Departure Board").click()
    expect(page.locator("h1")).to_contain_text("Departure Board")
    expect(page.locator("h4")).to_contain_text("No events to display")
    
    
    page.get_by_role("link", name=" Public Journey").click()
    page.get_by_role("link", name=test_data_tr1[0]['first_name']).click()
    time.sleep(2)
    
    page.get_by_role("button", name=" Follow User").click()
    expect(page.get_by_text("Successfully followed the")).to_be_visible()
    page.get_by_text("Successfully followed the").wait_for(state="hidden")
    
    
    page.get_by_role("button", name=" Follow Journey").click()
    expect(page.get_by_text("Successfully followed the")).to_be_visible()
    page.get_by_text("Successfully followed the").wait_for(state="hidden")
    
    
    page.get_by_role("link", name=" View").first.click()
    expect(page.get_by_role("heading", name="Event Details")).to_be_visible()
    page.get_by_role("button", name=" Follow Location").click()
    page.get_by_text("You are now following this").wait_for(state="hidden")
    
    page.get_by_role("link", name=" Departure Board").click()
    expect(page.locator("h1")).to_contain_text("Departure Board")
    
    # validation
    expect(page.get_by_role("main")).to_contain_text("Rosarios Journey")
    expect(page.get_by_role("main")).to_contain_text("Traveller_rosario1")
    expect(page.get_by_role("main")).to_contain_text("Australia")
    
    
    page.get_by_role("link", name="Journeys").click()
    page.get_by_role("link", name="Users").click()
    page.get_by_role("link", name="Locations").click()
    
    
    page.get_by_role("button", name=" Unfollow").first.click()
    # expect(page.get_by_text("Successfully unfollowed")).to_contain_text("Successfully unfollowed")
    # page.get_by_text("Successfully unfollowed").wait_for(state="hidden")
    # page.get_by_text("Following this location").wait_for(state="hidden")
   
    page.get_by_role("button", name=" Unfollow").first.click()
    # expect(page.get_by_text("Successfully unfollowed user")).to_contain_text("Successfully unfollowed user")
    # page.get_by_text("Successfully unfollowed user").wait_for(state="hidden")
    # page.get_by_text("Successfully unfollowed user").click()
    page.get_by_role("button", name=" Unfollow").click()
    # expect(page.get_by_text("Successfully unfollowed")).to_contain_text("Successfully unfollowed")
    # page.get_by_text("Successfully unfollowed").wait_for(state="hidden")
    
    
    # page.get_by_text("Successfully unfollowed").click()