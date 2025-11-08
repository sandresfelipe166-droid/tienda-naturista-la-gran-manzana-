# Example Usage of JWT Authentication

## 1. Obtain JWT Token

Use the login endpoint to get a token:

```bash
curl -X POST "http://localhost:8000/auth/login" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=yourusername&password=yourpassword"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 2. Use JWT Token in Requests

Include the token in the Authorization header:

```bash
curl -X GET "http://localhost:8000/api/v1/laboratorios" \\
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

This will authenticate the request and allow access to protected endpoints.

---

Replace `yourusername` and `yourpassword` with your actual credentials.

Make sure your server is running at `http://localhost:8000`.
