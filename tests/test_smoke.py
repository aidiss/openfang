def test_import():
    """Verify basic import works."""
    from openfang import settings

    assert settings is not None
