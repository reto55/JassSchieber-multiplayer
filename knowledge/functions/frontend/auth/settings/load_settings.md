---
type: Python Function
title: load_settings
resource: frontend/auth/settings.py#L27-L36
generated:
  by: okf-rs/0.3.0
relationships:
  called_by:
  - functions/ausbau/server/_ensure_auth_initialised
  - functions/tests/auth/test_settings/test_settings_required_fields
  - functions/tests/auth/test_settings/test_settings_missing_admin_bootstrap_raises
  - functions/tests/auth/test_settings/test_settings_secure_cookie_inferred_from_https
---

# Signature

`def load_settings() -> Settings:`

# Called by

- [_ensure_auth_initialised](../../../../functions/ausbau/server/_ensure_auth_initialised.md)
- [test_settings_required_fields](../../../../functions/tests/auth/test_settings/test_settings_required_fields.md)
- [test_settings_missing_admin_bootstrap_raises](../../../../functions/tests/auth/test_settings/test_settings_missing_admin_bootstrap_raises.md)
- [test_settings_secure_cookie_inferred_from_https](../../../../functions/tests/auth/test_settings/test_settings_secure_cookie_inferred_from_https.md)