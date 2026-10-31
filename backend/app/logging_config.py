import logging
from app import config


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("support-assistant")
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(console_handler)

    # Ship the same events to Splunk when HEC credentials are configured.
    # Left unconfigured, the service just logs to stdout — handy for local
    # dev and for platforms (like Docker/K8s) that already scrape stdout.
    if config.SPLUNK_HEC_URL and config.SPLUNK_HEC_TOKEN:
        try:
            from splunk_hec_handler import SplunkHecHandler

            hec_handler = SplunkHecHandler(
                config.SPLUNK_HEC_URL, config.SPLUNK_HEC_TOKEN,
                index="support_assistant", source="genai-support-assistant",
                ssl_verify=False,
            )
            logger.addHandler(hec_handler)
        except Exception as exc:  # pragma: no cover
            logger.warning("Could not attach Splunk handler: %s", exc)

    return logger
