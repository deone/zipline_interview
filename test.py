import unittest

from interview import OrderingSystem

class TestOrderingSystem(unittest.TestCase):
    def setUp(self):
        self.product_info = [
            {"mass_g": 700, "product_name": "RBC A+ Adult", "product_id": 0},
            {"mass_g": 700, "product_name": "RBC B+ Adult", "product_id": 1},
            {"mass_g": 300, "product_name": "FFP B+", "product_id": 11},
        ]
        self.restock = [
            {"product_id": 0, "quantity": 30},
            {"product_id": 1, "quantity": 25},
            {"product_id": 11, "quantity": 1}
        ]
        self.os = OrderingSystem(self.product_info)
        self.catalog = self.os.init_catalog()

    def test_init_catalog(self):
        # Test for catalog initialization
        self.assertEqual(self.catalog, {
            0: {"mass_g": 700, "product_name": "RBC A+ Adult", "quantity": 0},
            1: {"mass_g": 700, "product_name": "RBC B+ Adult", "quantity": 0},
            11: {"mass_g": 300, "product_name": "FFP B+", "quantity": 0}
        })

    def test_process_restock(self):
        inventory = self.os.process_restock(self.restock)

        # Test for restock
        self.assertEqual(inventory, {
            0: {'mass_g': 700, 'product_name': 'RBC A+ Adult', 'quantity': 30},
            1: {'mass_g': 700, 'product_name': 'RBC B+ Adult', 'quantity': 25},
            11: {"mass_g": 300, "product_name": "FFP B+", "quantity": 1}
        })

    def test_process_order_success(self):
        inventory = self.os.process_restock(self.restock)
        order = {"order_id": 123, "requested": [{"product_id": 11, "quantity": 1}, {"product_id": 1, "quantity": 2}]}
        shipment = self.os.process_order(order)

        # Test for shipment
        self.assertEqual(shipment['items'],
            [{'product_id': 11, 'quantity': 1}, {'product_id': 1, 'quantity': 2}]
        )
        self.assertEqual(shipment['order_id'], 123)
        self.assertEqual(shipment['mass_g'], 1700)

        # Test for inventory depletion
        self.assertEqual(inventory[11]['quantity'], 0)
        self.assertEqual(inventory[1]['quantity'], 23)

    def test_process_order_drone_weight_exceeded(self):
        inventory = self.os.process_restock(self.restock)
        order = {"order_id": 123, "requested": [{"product_id": 0, "quantity": 2}, {"product_id": 1, "quantity": 2}]}
        shipment = self.os.process_order(order)

        # Test for shipment
        self.assertEqual(shipment['items'],
            [{'product_id': 0, 'quantity': 2}]
        )
        self.assertEqual(shipment['order_id'], 123)
        self.assertEqual(shipment['mass_g'], 1400)

        # Test for inventory depletion
        self.assertEqual(inventory[0]['quantity'], 28)

        # Test for pending shipment
        self.assertEqual(len(self.os.pending_shipments), 1)
        self.assertEqual(self.os.pending_shipments[0]['order_id'], 123)
        self.assertEqual(self.os.pending_shipments[0]['items'], [{'product_id': 1, 'quantity': 2}])
        self.assertEqual(self.os.pending_shipments[0]['mass_g'], 1400)

    def test_process_order_product_unavailable(self):
        inventory = self.os.process_restock(self.restock)
        order = {"order_id": 123, "requested": [{"product_id": 0, "quantity": 2}, {"product_id": 10, "quantity": 4}]}
        shipment = self.os.process_order(order)

        # Test for shipment
        self.assertEqual(shipment['items'],
            [{'product_id': 0, 'quantity': 2}]
        )
        self.assertEqual(shipment['order_id'], 123)
        self.assertEqual(shipment['mass_g'], 1400)

        # Test for inventory depletion
        self.assertEqual(inventory[0]['quantity'], 28)

        # Test for pending order
        self.assertEqual(len(self.os.pending_orders), 1)
        self.assertEqual(self.os.pending_orders[0]['order_id'], 123)
        self.assertEqual(self.os.pending_orders[0]['requested'], [{'product_id': 10, 'quantity': 4}])

    def test_process_order_not_enough_in_inventory(self):
        inventory = self.os.process_restock(self.restock)
        order = {"order_id": 123, "requested": [{"product_id": 11, "quantity": 2}, {"product_id": 1, "quantity": 2}]}
        shipment = self.os.process_order(order)

        # Test for shipment
        self.assertEqual(shipment['items'],
            [{'product_id': 1, 'quantity': 2}]
        )
        self.assertEqual(shipment['order_id'], 123)
        self.assertEqual(shipment['mass_g'], 1400)

        # Test for inventory depletion
        self.assertEqual(inventory[1]['quantity'], 23)

        # Test for pending order
        self.assertEqual(len(self.os.pending_orders), 1)
        self.assertEqual(self.os.pending_orders[0]['order_id'], 123)
        self.assertEqual(self.os.pending_orders[0]['requested'], [{'product_id': 11, 'quantity': 2}])

if __name__ == "__main__":
    unittest.main()
