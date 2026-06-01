# connectors/ — Phase 6 connector framework.
#
# Each connector category defines an ABC in base/ and one or more
# provider implementations in providers/. The registry module reads
# site_config at runtime and returns the active provider instance.
#
# Usage:
#   from app.connectors.registry import get_email_connector
#   connector = get_email_connector()
#   connector.send_prayer_notification(...)
