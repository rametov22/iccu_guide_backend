__all__ = (
    "MARTOR_THEME",
    "MARTOR_ENABLE_CONFIGS",
    "MARTOR_TOOLBAR_BUTTONS",
    "MARTOR_MARKDOWN_BASE_MENTION_URL",
)


MARTOR_THEME = "bootstrap"

MARTOR_ENABLE_CONFIGS = {
    "emoji": "true",
    "imgur": "true",
    "mention": "false",
    "jquery": "true",
    "living": "false",
    "spellcheck": "false",
    "hljs": "true",
}

MARTOR_TOOLBAR_BUTTONS = [
    "bold",
    "italic",
    "horizontal",
    "heading",
    "pre-code",
    "blockquote",
    "unordered-list",
    "ordered-list",
    "link",
    "image-link",
    "direct-mention",
    "toggle-maximize",
    "help",
]

# Максимальная длина markdown
MARTOR_MARKDOWN_BASE_MENTION_URL = ""
