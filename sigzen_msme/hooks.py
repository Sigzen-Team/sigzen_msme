app_name = "sigzen_msme"
app_title = "Sigzen Msme"
app_publisher = "Sigzen Msme"
app_description = "Sigzen Msme"
app_email = "Sigzen@sigzen.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sigzen_msme/css/sigzen_msme.css"
# app_include_js = "/assets/sigzen_msme/js/sigzen_msme.js"

# include js, css files in header of web template
# web_include_css = "/assets/sigzen_msme/css/sigzen_msme.css"
# web_include_js = "/assets/sigzen_msme/js/sigzen_msme.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sigzen_msme/public/scss/website"

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
after_migrate = "sigzen_msme.install.after_install"
# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sigzen_msme.utils.jinja_methods",
# 	"filters": "sigzen_msme.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sigzen_msme.install.before_install"
# after_install = "sigzen_msme.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sigzen_msme.uninstall.before_uninstall"
# after_uninstall = "sigzen_msme.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sigzen_msme.utils.before_app_install"
# after_app_install = "sigzen_msme.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sigzen_msme.utils.before_app_uninstall"
# after_app_uninstall = "sigzen_msme.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sigzen_msme.notifications.get_notification_config"

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
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sigzen_msme.tasks.all"
# 	],
# 	"daily": [
# 		"sigzen_msme.tasks.daily"
# 	],
# 	"hourly": [
# 		"sigzen_msme.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sigzen_msme.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sigzen_msme.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sigzen_msme.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sigzen_msme.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sigzen_msme.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sigzen_msme.utils.before_request"]
# after_request = ["sigzen_msme.utils.after_request"]

# Job Events
# ----------
# before_job = ["sigzen_msme.utils.before_job"]
# after_job = ["sigzen_msme.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sigzen_msme.auth.validate"
# ]
