"""
Lightweight registry for open screen instances so pages can notify each other.

Usage:
	from screens import register_page, unregister_page, get_page
	register_page('calendar', calendar_page_instance)
	p = get_page('calendar')
"""
_PAGES = {}

def register_page(name, instance):
	_PAGES[name] = instance

def unregister_page(name):
	if name in _PAGES:
		del _PAGES[name]

def get_page(name):
	return _PAGES.get(name)
