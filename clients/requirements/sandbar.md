# Client: [Sandbar]

## Website: [https://app.dev.sandbar.ai]

## Workflow:
1. Navigate to homepage
2. Click login button
3. Enter username and password
4. Submit login form
5. Wait for 2FA phone push notification approval (manual - user taps "Yes" on phone, allow 30 seconds)
6. Navigate to customers page
6a. Open filters and select "Alert status: Open" to show only customers with open alerts
6b. Click "Load more" repeatedly until non-PEP customers are visible (may need multiple loads)
7. Click a customer far enough down on the page so it's not in the top 10, but NOT one marked as PEP
8. Wait for AI Summary to appear if not immediately visible (wait up to 5-7 seconds, it may or may not be present)
9. Read through the page and make a decision: is a match or is not a match. Use the page data and AI Summary (if present) to guide you.
10. Decision the person using keyboard shortcuts:
    - Press 'y' for match or 'n' for not a match
    - Press 'r' to specify match reason
    - Press 'd' to add details
    - Press Command+Enter (⌘+↵) to submit the decision
11. Return to the customers page.
12. Repeat steps 7-11 for exactly ONE more customer (2 customers total).
13. Click Logout under the upper left icon on the page.

## Selectors (if known):

## Notes:
- Website uses 2FA via phone push notification (not SMS code)
- Username and password are in .env: GOOGLE_LOGIN and GOOGLE_PW
- Rate limit: 10 requests per minute
- Session expires after 30 minutes
- Must accept cookies before login
- AI Summary may or may not be present on customer detail pages - wait 5-7 seconds only if not immediately visible