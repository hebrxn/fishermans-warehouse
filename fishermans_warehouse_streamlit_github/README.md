# Fisherman's Warehouse — Streamlit storefront

A branded Streamlit storefront prototype for Fisherman's Warehouse, Durban.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy using GitHub and Streamlit Community Cloud
1. Extract this project ZIP.
2. Upload the contents to a GitHub repository.
3. Visit https://share.streamlit.io/ and connect GitHub.
4. Select the repository and `app.py`, then deploy.

## Included
- Supplied Fisherman's Warehouse logo in `assets/logo.png`
- Responsive storefront styling, product search and categories
- Basket and delivery/collection enquiry workflow
- Product CSV import/export in Store Admin
- Local SQLite enquiry log

## Important integration status
This is a working storefront prototype, **not yet connected to live Digitot or The Courier Guy services**. The actual Digitot API/integration documentation and merchant credentials are not available yet. The Courier Guy API credentials and account-specific endpoint/schema are also required. No live stock, courier prices, payment processing or confirmed orders are claimed.

### Digitot next steps
Request from Digitot:
- API or approved integration/export documentation for your POS + Inventory version
- Authentication and test environment
- Product/price/stock read access
- Online order writeback support
- Webhook or sync frequency details

Digitot remains the stock source of truth. Once its supported interface is known, build and test a connector before enabling live shared stock.

### The Courier Guy next steps
Request merchant API credentials, rate/quote endpoint documentation, collection address setup, parcel field requirements and booking/waybill permissions. Configure only after confirming the account's current API specification.

## Before production
- Replace demonstration products/prices/stock with Digitot data.
- Confirm official store phone, email and WhatsApp details.
- Add login protection to Store Admin.
- Move order/enquiry storage to a persistent managed database before Streamlit deployment.
- Add payment gateway, courier booking, privacy/POPIA notice, terms, delivery and returns policies.
