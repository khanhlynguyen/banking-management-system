# config.py
# Database configuration 

DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'root',
    'password': '123456',   
    'database': 'BankingDB',
    'charset':  'utf8mb4',
}

APP_TITLE   = "NEU Banking Management System"
APP_VERSION = "v1.0"

# Color palette — Navy Banking Theme
COLORS = {
    'navy':         '#0A1628',
    'navy_mid':     '#112240',
    'navy_light':   '#1E3A5F',
    'accent':       '#2E86AB',
    'accent_light': '#4ECDC4',
    'gold':         '#F4A261',
    'white':        '#FFFFFF',
    'off_white':    '#F0F4F8',
    'gray':         '#8892A4',
    'gray_light':   '#CDD5DF',
    'success':      '#2ECC71',
    'warning':      '#F39C12',
    'danger':       '#E74C3C',
    'text_dark':    '#1A1A2E',
}

FONTS = {
    'title':    ('Georgia', 20, 'bold'),
    'subtitle': ('Georgia', 14, 'bold'),
    'heading':  ('Helvetica', 12, 'bold'),
    'body':     ('Helvetica', 11),
    'small':    ('Helvetica', 9),
    'mono':     ('Courier', 10),
    'amount':   ('Georgia', 13, 'bold'),
}
