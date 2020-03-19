def test_store_config_file(store):
    assert store.config_file().name == "sparse_store.yaml"
