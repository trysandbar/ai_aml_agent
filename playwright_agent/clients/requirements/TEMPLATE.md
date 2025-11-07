# Client: [Client Name Here]

## Website: [https://www.client-website.com]

## Workflow:
1. Navigate to homepage
2. Click login button
3. Enter username and password
4. Submit login form
5. Navigate to verification page
6. Extract verification status
7. Take screenshot of result
8. Logout
9. Stop when [specific condition - e.g., "logged out" or "auth rejected"]

## Selectors (if known):
- login_button: #login
- username_field: #username
- password_field: #password
- submit_button: button[type="submit"]

## Notes:
- Website uses 2FA (handle via SMS)
- Rate limit: 5 requests per minute
- Session expires after 30 minutes
- Must accept cookies before login
