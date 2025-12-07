from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(help_text='Order id from the e-commerce system.', max_length=64, unique=True)),
                ('customer_id', models.CharField(help_text='Reference to the customer in the e-commerce/CRM.', max_length=64)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled'), ('FULFILLMENT_REQUESTED', 'Fulfillment Requested'), ('COMPLETED', 'Completed')], default='PENDING', max_length=32)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='TND', max_length=3)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('ISSUED', 'Issued'), ('PAID', 'Paid'), ('CANCELLED', 'Cancelled')], default='ISSUED', max_length=32)),
                ('issued_at', models.DateTimeField(auto_now_add=True, null=True, blank=True)),
                ('paid_at', models.DateTimeField(null=True, blank=True)),
                ('payment_method', models.CharField(default='COD', help_text='Payment method (e.g., COD, ONLINE).', max_length=16)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='order_management.order')),
            ],
        ),
        migrations.CreateModel(
            name='FulfillmentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warehouse_code', models.CharField(help_text='Identifier for the warehouse that will fulfill this order.', max_length=32)),
                ('status', models.CharField(choices=[('CREATED', 'Created'), ('SENT_TO_WMS', 'Sent To Wms'), ('COMPLETED', 'Completed'), ('REJECTED', 'Rejected')], default='CREATED', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fulfillment_request', to='order_management.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=64)),
                ('product_name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order_management.order')),
            ],
        ),
    ]
