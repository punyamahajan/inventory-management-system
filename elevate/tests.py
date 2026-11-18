from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Category, Product, StockMovement


class HealthCheckAPITests(APITestCase):
    def test_healthy_response_when_database_is_connected(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"status": "healthy", "database": "connected"},
        )

    @patch("elevate.views.connection.cursor", side_effect=OperationalError)
    def test_unhealthy_response_when_database_is_unavailable(self, _cursor):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(
            response.data,
            {"status": "unhealthy", "database": "unavailable"},
        )

    def test_endpoint_does_not_require_authentication(self):
        unauthenticated_client = APIClient()

        response = unauthenticated_client.get(reverse("health-check"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticatedAPITestCase(APITestCase):
    """Common authenticated API setup and inventory factories."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="inventory-tester",
            email="inventory@example.com",
            password="test-password-123",
        )
        cls.category = Category.objects.create(
            name="Hardware", description="Physical inventory"
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def create_product(self, **overrides):
        values = {
            "sku": "SKU-001",
            "name": "Cordless Drill",
            "description": "A battery-powered drill",
            "category": self.category,
            "price": Decimal("129.99"),
            "stock_quantity": 12,
            "reorder_level": 5,
            "status": "active",
        }
        values.update(overrides)
        return Product.objects.create(**values)


class CategoryAPITests(AuthenticatedAPITestCase):
    def test_authenticated_category_creation(self):
        response = self.client.post(
            reverse("category-list-create"),
            {"name": "Office Supplies", "description": "Desk essentials"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(name="Office Supplies")
        self.assertEqual(category.description, "Desk essentials")
        self.assertEqual(response.data["id"], category.pk)
        self.assertEqual(response.data["product_count"], 0)

    def test_category_listing(self):
        Category.objects.create(name="Accessories")

        response = self.client.get(reverse("category-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            [item["name"] for item in response.data["results"]],
            ["Accessories", "Hardware"],
        )

    def test_category_retrieval(self):
        self.create_product()

        response = self.client.get(
            reverse("category-detail", kwargs={"pk": self.category.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Hardware")
        self.assertEqual(response.data["product_count"], 1)

    def test_duplicate_category_name_is_rejected(self):
        response = self.client.post(
            reverse("category-list-create"),
            {"name": "Hardware", "description": "Duplicate"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.filter(name="Hardware").count(), 1)


class ProductAPITests(AuthenticatedAPITestCase):
    def product_payload(self, **overrides):
        values = {
            "sku": "NEW-100",
            "name": "Safety Goggles",
            "description": "Clear protective eyewear",
            "category": self.category.pk,
            "price": "18.50",
            "stock_quantity": 20,
            "reorder_level": 4,
            "status": "active",
        }
        values.update(overrides)
        return values

    def test_authenticated_product_creation(self):
        response = self.client.post(
            reverse("product-list-create"), self.product_payload(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(sku="NEW-100")
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.price, Decimal("18.50"))
        self.assertEqual(response.data["category_name"], "Hardware")

    def test_product_listing(self):
        first = self.create_product()
        second = self.create_product(sku="SKU-002", name="Hammer")

        response = self.client.get(reverse("product-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            {item["id"] for item in response.data["results"]},
            {first.pk, second.pk},
        )

    def test_product_detail_retrieval(self):
        product = self.create_product()

        response = self.client.get(
            reverse("product-detail", kwargs={"pk": product.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["sku"], "SKU-001")
        self.assertEqual(response.data["description"], "A battery-powered drill")
        self.assertEqual(response.data["category_name"], "Hardware")
        self.assertFalse(response.data["needs_reorder"])

    def test_duplicate_sku_is_rejected(self):
        self.create_product(sku="DUPLICATE-1")

        response = self.client.post(
            reverse("product-list-create"),
            self.product_payload(sku="DUPLICATE-1"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sku", response.data)
        self.assertEqual(Product.objects.filter(sku="DUPLICATE-1").count(), 1)

    def test_product_search_matches_name_sku_and_description(self):
        matching = self.create_product(
            sku="TOOL-SEARCH", name="Precision Driver", description="For electronics"
        )
        self.create_product(sku="OTHER-1", name="Packing Tape", description="Shipping")

        for term in ("Precision", "TOOL-SEARCH", "electronics"):
            with self.subTest(term=term):
                response = self.client.get(
                    reverse("product-list-create"), {"search": term}
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data["count"], 1)
                self.assertEqual(response.data["results"][0]["id"], matching.pk)

    def test_product_category_filter(self):
        other_category = Category.objects.create(name="Consumables")
        matching = self.create_product(category=other_category)
        self.create_product(sku="SKU-002")

        response = self.client.get(
            reverse("product-list-create"), {"category": other_category.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], matching.pk)

    def test_low_stock_product_detection(self):
        low = self.create_product(stock_quantity=5, reorder_level=5)
        self.create_product(sku="SKU-002", stock_quantity=6, reorder_level=5)

        response = self.client.get(reverse("low-stock-products"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], low.pk)
        self.assertTrue(response.data["results"][0]["needs_reorder"])

    def test_product_status_filtering(self):
        inactive = self.create_product(status="inactive")
        self.create_product(sku="SKU-002", status="active")
        self.create_product(sku="SKU-003", status="discontinued")

        response = self.client.get(
            reverse("product-list-create"), {"status": "inactive"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], inactive.pk)


class StockMovementAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.product = self.create_product(stock_quantity=10)

    def test_stock_in_increases_product_stock_and_creates_movement(self):
        response = self.client.post(
            reverse("product-stock-in", kwargs={"pk": self.product.pk}),
            {"quantity": 7, "notes": "Supplier delivery"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 17)
        movement = StockMovement.objects.get(pk=response.data["id"])
        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.movement_type, "in")
        self.assertEqual(movement.quantity, 7)
        self.assertEqual(movement.notes, "Supplier delivery")

    def test_stock_out_decreases_product_stock_and_creates_movement(self):
        response = self.client.post(
            reverse("product-stock-out", kwargs={"pk": self.product.pk}),
            {"quantity": 4, "notes": "Customer order"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 6)
        movement = StockMovement.objects.get(pk=response.data["id"])
        self.assertEqual(movement.movement_type, "out")
        self.assertEqual(movement.quantity, 4)
        self.assertEqual(movement.notes, "Customer order")

    def test_stock_out_cannot_exceed_available_stock(self):
        response = self.client.post(
            reverse("product-stock-out", kwargs={"pk": self.product.pk}),
            {"quantity": 11},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Insufficient stock. Available: 10")
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)
        self.assertFalse(StockMovement.objects.exists())

    def test_stock_movement_creation_updates_stock(self):
        response = self.client.post(
            reverse("stock-movement-list-create"),
            {
                "product": self.product.pk,
                "movement_type": "in",
                "quantity": 3,
                "notes": "Manual receipt",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 13)
        self.assertEqual(response.data["product_sku"], self.product.sku)
        self.assertEqual(response.data["movement_type"], "in")

    def test_stock_movement_listing(self):
        first = StockMovement.objects.create(
            product=self.product, movement_type="in", quantity=2
        )
        second = StockMovement.objects.create(
            product=self.product, movement_type="out", quantity=1
        )

        response = self.client.get(reverse("stock-movement-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(
            [item["id"] for item in response.data["results"]],
            [second.pk, first.pk],
        )


class APIPermissionTests(APITestCase):
    """All inventory endpoints require an authenticated user.

    SessionAuthentication is the first configured authenticator, so DRF reports
    anonymous permission denials as 403 (it has no WWW-Authenticate header).
    """

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Protected Category")
        cls.product = Product.objects.create(
            sku="PROTECTED-1",
            name="Protected Product",
            category=cls.category,
            price=Decimal("10.00"),
            stock_quantity=5,
        )

    def test_unauthenticated_requests_are_rejected_for_protected_endpoints(self):
        requests = [
            ("get", reverse("category-list-create"), None),
            ("post", reverse("category-list-create"), {"name": "No Access"}),
            ("get", reverse("category-detail", kwargs={"pk": self.category.pk}), None),
            ("get", reverse("product-list-create"), None),
            ("post", reverse("product-list-create"), {}),
            ("get", reverse("product-detail", kwargs={"pk": self.product.pk}), None),
            ("get", reverse("low-stock-products"), None),
            ("get", reverse("stock-movement-list-create"), None),
            ("post", reverse("stock-movement-list-create"), {}),
            ("post", reverse("product-stock-in", kwargs={"pk": self.product.pk}), {"quantity": 1}),
            ("post", reverse("product-stock-out", kwargs={"pk": self.product.pk}), {"quantity": 1}),
        ]

        unauthenticated_client = APIClient()
        for method, url, data in requests:
            with self.subTest(method=method, url=url):
                response = getattr(unauthenticated_client, method)(
                    url, data=data, format="json"
                )
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
