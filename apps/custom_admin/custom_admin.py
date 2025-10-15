from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static



UNFOLD = {
    "DASHBOARD_TEMPLATE": "dashboard.html",
    "SITE_TITLE": "Admin Dashboard",
    "SITE_HEADER": "Administration",
    "SITE_URL": "/admin/",
    "SITE_SYMBOL": "admin_panel_settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "THEME": "light",
    "ACTIONS": {
        "ENABLE_DELETE": True,
        "ENABLE_ADD": True,
        "ENABLE_CHANGE": True,
        "ENABLE_BULK_DELETE": True,
    },

    "ENVIRONMENT": "development",

    "LOGIN": {
        "redirect_after": lambda request: "/admin/",
    },

    "STYLES": [lambda request: static("css/custom_admin.css")],
    "SCRIPTS": [lambda request: static("js/custom_admin.js")],

    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {"en": "🇺🇸", "bn": "🇧🇩"},
        },
    },

    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
        {
            "title": "Dashboard",
            "icon": "dashboard",
            "separator": True,
            "collapsible": False,
            "items": [
                {"title": "Admin Dashboard", "icon": "dashboard", "link": "/admin/"},
            ],
        },
            
            {
                "title": _("User Management"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Admins"), "icon": "verified_user", "link": "/admin/auths/customuser/admins/"},
                    {"title": _("Staff Members"), "icon": "supervisor_account", "link": "/admin/auths/customuser/staff/"},
                    {"title": _("Regular Users"), "icon": "person", "link": "/admin/auths/customuser/users/"},
                    {"title": _("Groups"), "icon": "group", "link": "/admin/auth/group/"},
                    {"title": _("Contact Messages"), "icon": "contact_mail", "link": "/admin/auths/contactmessage/"},
                    {"title": _("Help Us Improve"), "icon": "feedback", "link": "/admin/auths/helpusimprove/"},
                ],
            },

            {
                "title": _("Products & Shops"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Categories"), "icon": "category", "link": "/admin/products/category/"},
                    {"title": _("Packages"), "icon": "inventory", "link": "/admin/products/package/"},
                    {"title": _("Shops"), "icon": "store", "link": "/admin/products/shop/"},
                    {"title": _("Reviews"), "icon": "reviews", "link": "/admin/products/review/"},
                ],
            },
            {
                "title": _("Blogs"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("All Blogs"), "icon": "article", "link": "/admin/blogs/blog/"},
                ],
            },
            {
                "title": _("Bookings & Payments"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Bookings"), "icon": "book_online", "link": "/admin/booking/booking/"},
                    {"title": _("Payments"), "icon": "payment", "link": "/admin/booking/payment/"},
                ],
            },
           {
                "title": _("Cart & Coupons"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Carts"), "icon": "shopping_cart", "link": "/admin/cart/cart/"},
                    {"title": _("Coupons"), "icon": "local_offer", "link": "/admin/coupon/coupon/"},
                    {"title": _("Coupon Email Logs"), "icon": "mail", "link": "/admin/coupon/couponemaillog/"},
                ],
            },


            {
                "title": _("Notifications"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("All Notifications"), "icon": "notifications", "link": "/admin/notification/notification/"},
                ],
            },
        ],
    },

    "TABS": [
        {
            "models": ["auths.customuser"],
            "items": [
                {"title": _("All Users"), "link": "/admin/auths/customuser/"},
                {"title": _("Active"), "link": "/admin/auths/customuser/?is_active__exact=1"},
                {"title": _("Verified"), "link": "/admin/auths/customuser/?is_verified__exact=1"},
            ],
        },
        {
            "models": ["blogs.blog"],
            "items": [
                {"title": _("Published"), "link": "/admin/blogs/blog/?blog_status__exact=published"},
                {"title": _("Pending"), "link": "/admin/blogs/blog/?blog_status__exact=pending"},
                {"title": _("Drafts"), "link": "/admin/blogs/blog/?blog_status__exact=draft"},
            ],
        },
    ],
}





SUMMERNOTE_CONFIG = {
    'iframe': True,
    'summernote': {
        'width': '100%',
        'height': '300px',
    },
}