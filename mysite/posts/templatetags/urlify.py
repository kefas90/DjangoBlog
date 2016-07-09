from urllib.parse import quote_plus
from django import template

register = template.Library

# that's for twitter


@register.filter
def urlify(value):
    # we can use in templates as share_links (twitter) templates
    # instance.content|urlify as share_links - the same
    return quote_plus(value)
