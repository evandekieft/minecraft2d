class TestInventory:
    def test_inventory_initialization(self):
        player = Player()
        assert player.inventory == Inventory({}, 0)

    def test_add_to_inventory_new_item(self):
        player = Player()
        player.add_to_inventory("tree")

        assert player.inventory["tree"] == 1

    def test_add_to_inventory_existing_item(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("tree")

        assert player.inventory["tree"] == 2

    def test_add_multiple_item_types(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        player.add_to_inventory("tree")

        assert player.inventory["tree"] == 2
        assert player.inventory["grass"] == 1

    def test_get_top_inventory_items_empty(self):
        player = Player()
        top_items = player.get_top_inventory_items(5)

        assert top_items == []

    def test_get_top_inventory_items_sorted(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        player.add_to_inventory("tree")
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")

        top_items = player.get_top_inventory_items(5)

        assert top_items == [("tree", 3), ("grass", 2)]

    def test_get_top_inventory_items_limit(self):
        player = Player()
        for i in range(10):
            for j in range(i + 1):
                player.add_to_inventory(f"block_{i}")

        top_items = player.get_top_inventory_items(3)

        assert len(top_items) == 3

    def test_get_active_block_type_empty(self):
        player = Player()
        assert player.get_active_block_type() is None

    def test_get_active_block_type_valid(self):
        player = Player()
        player.add_to_inventory("tree")
        player.add_to_inventory("grass")
        player.active_slot = 0

        assert player.get_active_block_type() == "tree"

    def test_get_active_block_type_out_of_range(self):
        player = Player()
        player.add_to_inventory("tree")
        player.active_slot = 5

        assert player.get_active_block_type() is None
