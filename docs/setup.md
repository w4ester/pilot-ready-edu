# Development Setup Notes

## Seed Demo Account

To provision the demo teacher account used during local runs, execute the following SQL against your Postgres database (adjust the connection string as needed):

```sql
INSERT INTO user_profile (id, name, email, role, created_at, updated_at)
VALUES (
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  'Demo Teacher',
  'teacher@edinfinite.com',
  'teacher',
  now_ms(),
  now_ms()
)
ON CONFLICT (id) DO UPDATE
  SET name = EXCLUDED.name,
      email = EXCLUDED.email,
      updated_at = now_ms();

INSERT INTO user_auth (id, email, password, is_active, created_at, updated_at)
VALUES (
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  'teacher@edinfinite.com',
  '$2b$12$yVnESJNhpCHfKzd.5Bv4LOifYzKtMV3xWbjpr6K6I9O8Nj4Bx65WG',
  TRUE,
  now_ms(),
  now_ms()
)
ON CONFLICT (id) DO UPDATE
  SET email = EXCLUDED.email,
      password = EXCLUDED.password,
      is_active = EXCLUDED.is_active,
      updated_at = now_ms();
```

The password for this account is `2500`. After running the statements, verify the login flow with:

```bash
curl -i -X POST http://localhost:3434/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "teacher@edinfinite.com", "password": "2500"}'
```

A `200 OK` response confirms the account is ready for the frontend demo login.
