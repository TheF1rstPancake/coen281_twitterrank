"""
Default logger for the application.

Uses the built in Python logging module
along with a 3rd party module called *coloredlogs* to generate logs.
"""
import logging
USE_COLORED_LOGS = True
try:
    import coloredlogs
except ImportError as e:
    USE_COLORED_LOGS = False
# initialize logging
logger = logging.getLogger("twitterrank")
logger.setLevel(logging.INFO)

# initialize colored logs
log_format = "[%(asctime)s %(process)d %(name)s] [%(module)s:%(lineno)d] %(levelname).1s %(message)s"
formatter = logging.Formatter(log_format)
field_styles = {'process': {'color': 'magenta'},
                'module': {'color': 'cyan'},
                'name': {'color': 'blue'},
                'levelname': {'color': 'white', 'bold': True},
                'asctime': {'color': 'green'}
                }

if USE_COLORED_LOGS:
    coloredlogs.install(
        level="INFO",
        field_styles=field_styles,
        fmt=log_format)
else:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
