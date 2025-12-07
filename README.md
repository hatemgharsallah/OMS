# OMS

Order Management System (Django REST API).

## Local setup
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```

## Running tests
After activating the virtual environment and installing dependencies, run:
```bash
python manage.py test
```

## API documentation (Swagger / ReDoc)
Interactive docs are available once the server is running:

- JSON/YAML schema: `GET /swagger.json` or `GET /swagger.yaml`
- Swagger UI: `GET /swagger/`
- ReDoc: `GET /redoc/`

These endpoints are exposed by `drf-yasg` and require no authentication in this setup.

## cURL walkthrough
Example happy-path flow hitting each endpoint (base URL `http://localhost:8000/api/`):

1. **Create order**
   ```bash
   curl -X POST http://localhost:8000/api/orders/create \
     -H "Content-Type: application/json" \
     -d '{
       "external_id": "WEB-ORDER-00123",
       "customer_id": "CUST-999",
       "total_amount": 120.50,
       "currency": "TND",
       "items": [
         {"product_id": "SKU-123", "product_name": "Smartphone X", "quantity": 1, "unit_price": 100.00},
         {"product_id": "SKU-456", "product_name": "Phone Case", "quantity": 1, "unit_price": 20.50}
       ]
     }'
   ```
   *Expected*: `201 Created` with the order payload and `status: "PENDING"`.

2. **Confirm order** (replace `1` with the created order ID):
   ```bash
   curl -X PATCH http://localhost:8000/api/orders/update/1 \
     -H "Content-Type: application/json" \
     -d '{"status": "CONFIRMED"}'
   ```
   *Expected*: `200 OK` with `status: "CONFIRMED"`.

3. **Create invoice**
   ```bash
   curl -X POST http://localhost:8000/api/oms/invoice \
     -H "Content-Type: application/json" \
     -d '{"order": 1, "amount": 120.50, "payment_method": "COD"}'
   ```
   *Expected*: `201 Created` with invoice data and `status: "ISSUED"`.

4. **Create fulfillment request**
   ```bash
   curl -X POST http://localhost:8000/api/oms/fulfillment \
     -H "Content-Type: application/json" \
     -d '{"order": 1, "warehouse_code": "WH-SFAX"}'
   ```
   *Expected*: `201 Created`, fulfillment `status: "CREATED"`, and order status moves to `"FULFILLMENT_REQUESTED"`.
