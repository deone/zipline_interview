# zipline_interview
Pending orders and pending shipments are made pending for now. They are not processed.

Pending orders happen when there isn't enough of an item in inventory or when an item is unavailable.
Pending shipments happen when drone weight capacity is reached, and they are pending shipments because they have already been packaged.

An interesting update will be splitting an order item based on weight constraints or unavailability of inventory. e.g shipping 3 out of an order item requesting 10.
