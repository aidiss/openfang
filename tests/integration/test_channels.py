"""Integration tests for channel registry."""

from unittest.mock import AsyncMock

import pytest

from openfang.channels.models import ChannelAccount
from openfang.channels.registry import ChannelRegistry

# MockChannel fixture comes from conftest.py


class TestChannelRegistry:
    """Test channel registry operations."""

    @pytest.fixture
    def registry(self):
        return ChannelRegistry()

    def test_register_channel(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        assert registry.get_channel("telegram") is mock_channel
        assert registry.get_channel("unknown") is None

    def test_list_channels(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        channels = registry.list_channels()
        assert len(channels) == 1
        assert channels[0].id == "telegram"

    async def test_add_account(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        account = ChannelAccount(
            id="acc-1",
            channel_id="telegram",
            name="My Bot",
            config={"token": "secret"},
        )
        await registry.add_account(account)

        accounts = await registry.list_accounts()
        assert len(accounts) == 1
        assert accounts[0].id == "acc-1"

    async def test_add_account_unknown_channel(self, registry):
        account = ChannelAccount(
            id="acc-1",
            channel_id="unknown",
            name="My Bot",
            config={},
        )

        with pytest.raises(ValueError, match="Unknown channel"):
            await registry.add_account(account)

    async def test_remove_account(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        await registry.add_account(account)
        await registry.remove_account("telegram", "acc-1")

        accounts = await registry.list_accounts()
        assert len(accounts) == 0

    async def test_remove_account_stops_channel(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        await registry.add_account(account)
        await registry.remove_account("telegram", "acc-1")

        # FakeChannel tracks stopped accounts in _stopped set
        assert "acc-1" in mock_channel._stopped

    async def test_start_account(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        await registry.add_account(account)
        await registry.start_account("telegram", "acc-1")

        # FakeChannel tracks started accounts in _started set
        assert "acc-1" in mock_channel._started

    async def test_start_account_unknown_channel(self, registry):
        with pytest.raises(ValueError, match="Unknown channel"):
            await registry.start_account("unknown", "acc-1")

    async def test_start_account_unknown_account(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        with pytest.raises(ValueError, match="Unknown account"):
            await registry.start_account("telegram", "unknown")

    async def test_stop_account(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        await registry.add_account(account)
        await registry.stop_account("telegram", "acc-1")

        # FakeChannel tracks stopped accounts in _stopped set
        assert "acc-1" in mock_channel._stopped

    async def test_status(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        await registry.add_account(account)

        # Start the account first so it reports as connected
        await registry.start_account("telegram", "acc-1")

        statuses = await registry.status()
        assert len(statuses) == 1
        assert statuses[0].connected is True

    async def test_status_with_error(self, registry, mock_channel):
        mock_channel.status = AsyncMock(side_effect=Exception("Connection failed"))
        registry.register_channel(mock_channel)

        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        await registry.add_account(account)

        statuses = await registry.status()
        assert len(statuses) == 1
        assert "Connection failed" in statuses[0].last_error

    async def test_list_accounts_by_channel(self, registry, mock_channel):
        from tests.conftest import MockChannel

        ch2 = MockChannel("slack", "Slack")
        registry.register_channel(mock_channel)
        registry.register_channel(ch2)

        await registry.add_account(ChannelAccount(id="tg-1", channel_id="telegram", name="TG Bot", config={}))
        await registry.add_account(ChannelAccount(id="sl-1", channel_id="slack", name="Slack Bot", config={}))

        tg_accounts = await registry.list_accounts("telegram")
        assert len(tg_accounts) == 1
        assert tg_accounts[0].id == "tg-1"

        all_accounts = await registry.list_accounts()
        assert len(all_accounts) == 2

    def test_get_account(self, registry, mock_channel):
        registry.register_channel(mock_channel)

        # Manually add since get_account is sync
        account = ChannelAccount(id="acc-1", channel_id="telegram", name="Bot", config={})
        registry._accounts["telegram:acc-1"] = account

        found = registry.get_account("telegram", "acc-1")
        assert found is account

        not_found = registry.get_account("telegram", "missing")
        assert not_found is None
