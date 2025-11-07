# Client: Amazon.com

## Website: https://www.amazon.com

## Workflow:
1. Navigate to Amazon homepage
2. Search for "mechanical keyboard"
3. Click first product in results
4. Add product to cart
5. Proceed to checkout
6. Stop when authentication/login required

## Selectors (if known):
- search_box: #twotabsearchtextbox OR #nav-bb-search
- search_button: #nav-search-submit-button

## Notes:
- Selectors change frequently - use dynamic detection
- Rate limit: 5 requests per minute
- May show protection plan popup after add to cart
- Checkout requires Amazon account (expect auth rejection)
