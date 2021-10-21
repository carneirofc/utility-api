import logging
from datetime import date

from flask.app import Flask


def get_logger(name=__name__, level=logging.INFO):
    """Returns a logger object"""

    logger = logging.getLogger(name)

    if not len(logger.handlers):
        logger.setLevel(level)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(name)s %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s] %(message)s"
        )
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger


def get_app_rules(app: Flask):
    rules = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods)) if rule.methods else ""
        rules.append(
            {
                "endpoint": rule.endpoint,
                "methods": methods,
                "name": str(rule),
            }
        )
    rules_sorted = sorted(rules, key=lambda x: x["name"])
    return rules_sorted


def date_today_str() -> str:

    today = date.today()

    # dd/mm/YY
    return today.strftime("%Y-%m-%d")
