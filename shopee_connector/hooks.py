from . import __version__ as app_version

app_name = "shopee_connector"
app_title = "Shopee Connector"
app_publisher = "DAS"
app_description = "Shopee"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "DAS@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/shopee_connector/css/shopee_connector.css"
# app_include_js = "/assets/shopee_connector/js/shopee_connector.js"

# include js, css files in header of web template
# web_include_css = "/assets/shopee_connector/css/shopee_connector.css"
# web_include_js = "/assets/shopee_connector/js/shopee_connector.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "shopee_connector/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "shopee_connector.install.before_install"
# after_install = "shopee_connector.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "shopee_connector.uninstall.before_uninstall"
# after_uninstall = "shopee_connector.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "shopee_connector.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"shopee_connector.tasks.all"
# 	],
# 	"daily": [
# 		"shopee_connector.tasks.daily"
# 	],
# 	"hourly": [
# 		"shopee_connector.tasks.hourly"
# 	],
# 	"weekly": [
# 		"shopee_connector.tasks.weekly"
# 	]
# 	"monthly": [
# 		"shopee_connector.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "shopee_connector.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "shopee_connector.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "shopee_connector.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"shopee_connector.auth.validate"
# ]

