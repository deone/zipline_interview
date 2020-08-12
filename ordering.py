import copy
import random
"""
product_info = [
    {"mass_g": 700, "product_name": "RBC A+ Adult", "product_id": 0},
    {"mass_g": 700, "product_name": "RBC B+ Adult", "product_id": 1},
    {"mass_g": 750, "product_name": "RBC AB+ Adult", "product_id": 2},
    {"mass_g": 680, "product_name": "RBC O- Adult", "product_id": 3},
    {"mass_g": 350, "product_name": "RBC A+  Child", "product_id": 4},
    {"mass_g": 200, "product_name": "RBC AB+ Child", "product_id": 5},
    {"mass_g": 120, "product_name": "PLT AB+", "product_id": 6},
    {"mass_g": 80, "product_name": "PLT O+", "product_id": 7},
    {"mass_g": 80, "product_name": "CRYO AB+", "product_id": 9},
    {"mass_g": 300, "product_name": "FFP A+", "product_id": 10},
    {"mass_g": 300, "product_name": "FFP B+", "product_id": 11},
    {"mass_g": 300, "product_name": "FFP AB+", "product_id": 12},
    {"mass_g": 40, "product_name": "CRYO A+", "product_id": 8},
]

restock = [{"product_id": 0, "quantity": 30}, {"product_id": 1, "quantity": 25}, {"product_id": 2, "quantity": 25}, {"product_id": 3, "quantity": 12}, {"product_id": 4, "quantity": 15}, {"product_id": 5, "quantity": 10}, {"product_id": 6, "quantity": 8}, {"product_id": 7, "quantity": 8}, {"product_id": 8, "quantity": 20}, {"product_id": 9, "quantity": 10}, {"product_id": 10, "quantity": 5}, {"product_id": 11, "quantity": 5}, {"product_id": 12, "quantity": 5}]

order = {"order_id": 123, "requested": [{"product_id": 0, "quantity": 2}, {"product_id": 10, "quantity": 4}]}

shipment = {"order_id": 123, "shipped": [{"product_id": 0, "quantity": 1}, {"product_id": 10, "quantity": 2}]}
"""

class OrderingSystem:
    def __init__(self, product_info):
        self.product_info = product_info
        self.catalog = {}
        self.inventory = {}
        self.pending_shipments = []
        self.pending_orders = []

    def init_catalog(self):
        # Takes a list of items containing products that can be ordered
        # and initializes catalog, basically copying over item names and setting quantity to 0.
        for p in self.product_info:
            self.catalog[p['product_id']] = {
                'mass_g': p['mass_g'],
                'product_name': p['product_name'],
                'quantity': 0
            }

        return self.catalog

    def process_restock(self, restock):
        # Takes a list of items to restock and increases the quantity
        # of each item in the catalog by restock quantity
        self.inventory = self.catalog
        for r in restock:
            existing_qty = self.catalog[r['product_id']]['quantity']
            new_qty = r['quantity']
            self.inventory[r['product_id']]['quantity'] = existing_qty + new_qty
        return self.inventory

    def process_order(self, order):
        # Takes an order, performs weight and availability checks, reduces inventory quantity,
        # returns shipment(s), and stores pending items to be shipped
        # if there are any
        shipment = {
            'id': random.randint(100, 999),
            'order_id': order['order_id'],
            'items': [],
            'mass_g': 0
        }
        pending_shipment = copy.deepcopy(shipment)
        pending_order = {
            'order_id': order['order_id'],
            'requested': []
        }

        for item in order['requested']:
            pid = item['product_id']
            if pid in self.inventory:
                inv_item = self.inventory[pid]
                item_mass = inv_item['mass_g'] * item['quantity']

                # Check quantity and weight
                if item['quantity'] <= inv_item['quantity']:
                    if (shipment['mass_g'] + item_mass) < 1800:
                        # print('Order successful. Items packaged.')
                        shipment['items'].append(item)
                        shipment['mass_g'] = shipment['mass_g'] + item_mass
                    else:
                        # print('Drone weight capacity reached. Item added to pending shipments')
                        pending_shipment['items'].append(item)
                        pending_shipment['mass_g'] = item_mass
                        self.pending_shipments.append(pending_shipment)

                    # Update inventory
                    # This happens when items are available in the requested quantity,
                    # even if we've reached drone weight capacity.
                    inv_item['quantity'] = inv_item['quantity'] - item['quantity']
                    self.inventory[pid] = inv_item
                else:
                    # print('Not enough in inventory. Added to pending orders', item)
                    pending_order['requested'].append(item)
                    self.pending_orders.append(pending_order)
            else:
                # print('Item unavailable. Added to pending orders', item)
                pending_order['requested'].append(item)
                self.pending_orders.append(pending_order)
        return shipment

    def ship_package(self, shipment):
        print('{} {} {} {} {}'.format(
            'Package',
            str(shipment['id']),
            'belonging to order',
            str(shipment['order_id']),
            'has been shipped.'
        ))

if __name__ == "__main__":
    product_info = [
        {"mass_g": 700, "product_name": "RBC A+ Adult", "product_id": 0},
        {"mass_g": 700, "product_name": "RBC B+ Adult", "product_id": 1},
        {"mass_g": 300, "product_name": "FFP B+", "product_id": 11},
    ]
    os = OrderingSystem(product_info)
    catalog = os.init_catalog()
    print('Catalog:', catalog)

    restock = [
        {"product_id": 0, "quantity": 30},
        {"product_id": 1, "quantity": 25},
        {"product_id": 11, "quantity": 1}
    ]
    inventory = os.process_restock(restock)
    print('Inventory:', inventory)

    # Product ID 10 unavailable - we need to restock
    # order = {"order_id": 123, "requested": [{"product_id": 0, "quantity": 2}, {"product_id": 10, "quantity": 4}]}

    # Drone weight exceeded - added to pending shipments
    # order = {"order_id": 123, "requested": [{"product_id": 0, "quantity": 2}, {"product_id": 1, "quantity": 2}]}

    # Items available in requested quantity and within drone weight limit
    # order = {"order_id": 123, "requested": [{"product_id": 11, "quantity": 1}, {"product_id": 1, "quantity": 2}]}

    # Not enough quantity in inventory - added to pending orders
    # order = {"order_id": 123, "requested": [{"product_id": 11, "quantity": 2}, {"product_id": 1, "quantity": 2}]}

    shipment = os.process_order(order)
    print('Shipment:', shipment)
    print('New inventory:', os.inventory)
    print('Pending orders:', os.pending_orders)
    print('Pending shipments:', os.pending_shipments)
    os.ship_package(shipment)
