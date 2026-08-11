---
type: Python Module
title: test_passwords
resource: tests/auth/test_passwords.py#L1-L31
generated:
  by: okf-rs/0.3.0
relationships:
  imports:
  - external/pytest
  - external/frontend-auth-passwords
---

# Contains

- [test_min_length](../../../functions/tests/auth/test_passwords/test_min_length.md)
- [test_common_password_rejected](../../../functions/tests/auth/test_passwords/test_common_password_rejected.md)
- [test_contains_username_rejected](../../../functions/tests/auth/test_passwords/test_contains_username_rejected.md)
- [test_contains_email_local_part_rejected](../../../functions/tests/auth/test_passwords/test_contains_email_local_part_rejected.md)
- [test_long_unique_password_passes](../../../functions/tests/auth/test_passwords/test_long_unique_password_passes.md)
- [test_long_password_no_truncation_at_72_bytes](../../../functions/tests/auth/test_passwords/test_long_password_no_truncation_at_72_bytes.md)

# Imports

- `pytest`
- `frontend.auth.passwords`