class Config:
    """ Default role & status assigned to new users upon registration. """
    DEFAULT_USER_ROLE = 'traveller'
    DEFAULT_USER_STATUS = 'active'
    """ Default image folder, image extensions allowed, and maximum file size for uploads. """
    UPLOAD_FOLDER_PROFILE = 'uploads/profile'
    UPLOAD_FOLDER_EVENT = 'uploads/events'
    UPLOAD_FOLDER_JOURNEY = 'uploads/journey'
    UPLOAD_FOLDER_STAFF_REMOVE_IMAGE = 'uploads/staff_remove_image'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit
    MAX_EVENT_IMAGE_COUNT = 5
    """ Email regex pattern, maximum email length, and password character requirements. """
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    EMAIL_LENGTH = 50
    PASSWORD_CHAR = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
    """ Announcements """
    ANNOUNCEMENT_PAGE_LIMIT = 5
    """ Subscription Notification """
    SUBSCRIPTION_PAGE_LIMIT = 5
    """ Edit log messages """
    EDIT_LOG_PAGE_LIMIT = 5
    """ Homepage """
    HOMEPAGE_JOURNEY_LIMIT = 5
    """ Journey """
    JOURNEY_PAGE_LIMIT = 6
    JOURNEY_STATUS = ['private','public','published']
    # ？？gift reasons  (e.g., "High-quality content", "Popular travel blogger", "Bad Experience")
    """ Achievement """
    ACHIEVEMENT_LEADERBOARD_TOP_LIMIT = 10
    ACHIEVEMENT_LEADERBOARD_RECENT_LIMIT = 10
    ACHIEVEMENT_TYPE_1_TARGET_VALUE = 1  # Creating the First Journey
    ACHIEVEMENT_TYPE_2_TARGET_VALUE = 1  # Creating the First Event
    ACHIEVEMENT_TYPE_3_TARGET_VALUE = 1  # Creating the Journey as Public
    ACHIEVEMENT_TYPE_4_TARGET_VALUE = 20  # Visit More Than 20 Locations
    ACHIEVEMENT_TYPE_5_TARGET_VALUE = 30  # Longest Journey
    ACHIEVEMENT_TYPE_6_TARGET_VALUE = 5  # View a Newly Shared Journey
    ACHIEVEMENT_TYPE_7_TARGET_VALUE = 1  # First Report Submitted
    ACHIEVEMENT_TYPE_8_TARGET_VALUE = 1  # Make Comment on the Bug/Help/Appeal Request
    ACHIEVEMENT_TYPE_9_TARGET_VALUE = 5  # Create at Least 5 Bug/Help/Appeal Request
    ACHIEVEMENT_TYPE_10_TARGET_VALUE = 1  # view the complete edit history of my shared journeys and events
    ACHIEVEMENT_TYPE_11_TARGET_VALUE = 1  # create first "No Edit" journey
    ACHIEVEMENT_TYPE_12_TARGET_VALUE = 1  # follow first "shared journey"
    ACHIEVEMENT_TYPE_13_TARGET_VALUE = 1  # follow any user who is shared his journey public
    ACHIEVEMENT_TYPE_14_TARGET_VALUE = 1  # first journey a user Publishes on the homepage
    ACHIEVEMENT_TYPE_15_TARGET_VALUE = 5  # Earn an achievement when adding a Cover Image to five journeys.