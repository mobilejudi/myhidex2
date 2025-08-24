import pytest
from unittest.mock import AsyncMock
from risk.engine import spl_mint_risk, honeypot_simulation

@pytest.mark.asyncio
async def test_spl_mint_risk_safe_token(mocker):
    """Tests spl_mint_risk with a safe token (no authorities)."""
    mock_get_account_info = mocker.patch(
        "risk.engine.get_account_info",
        new_callable=AsyncMock,
        return_value={
            "value": {
                "data": {
                    "parsed": {
                        "info": {
                            "mintAuthority": None,
                            "freezeAuthority": None,
                            "supply": "1000000",
                            "decimals": 9,
                        }
                    }
                }
            }
        },
    )

    risk_info = await spl_mint_risk("some_mint_address")
    assert risk_info["mint_active"] is False
    assert risk_info["freeze_active"] is False
    assert risk_info["supply"] == 1000000
    mock_get_account_info.assert_awaited_once()

@pytest.mark.asyncio
async def test_spl_mint_risk_risky_token(mocker):
    """Tests spl_mint_risk with a risky token (both authorities active)."""
    mock_get_account_info = mocker.patch(
        "risk.engine.get_account_info",
        new_callable=AsyncMock,
        return_value={
            "value": {
                "data": {
                    "parsed": {
                        "info": {
                            "mintAuthority": "some_authority_address",
                            "freezeAuthority": "some_authority_address",
                            "supply": "1000000",
                            "decimals": 9,
                        }
                    }
                }
            }
        },
    )

    risk_info = await spl_mint_risk("some_mint_address")
    assert risk_info["mint_active"] is True
    assert risk_info["freeze_active"] is True

@pytest.mark.asyncio
async def test_spl_mint_risk_account_not_found(mocker):
    """Tests spl_mint_risk when the account info is not found."""
    mock_get_account_info = mocker.patch(
        "risk.engine.get_account_info",
        new_callable=AsyncMock,
        return_value=None,
    )

    risk_info = await spl_mint_risk("some_mint_address")
    # Should return default/false values if account info is missing
    assert risk_info["mint_active"] is False
    assert risk_info["freeze_active"] is False
    assert risk_info["supply"] == 0

@pytest.mark.asyncio
async def test_honeypot_simulation_tradable():
    """Tests honeypot_simulation with a valid, tradable quote."""
    jupiter_quote = {
        "data": [
            {"priceImpactPct": 0.05} # 5% price impact
        ]
    }
    tradable, impact_bps = await honeypot_simulation(jupiter_quote)
    assert tradable is True
    assert impact_bps == 500 # 0.05 * 10000

@pytest.mark.asyncio
async def test_honeypot_simulation_not_tradable():
    """Tests honeypot_simulation with no valid route."""
    jupiter_quote = {"data": []}
    tradable, impact_bps = await honeypot_simulation(jupiter_quote)
    assert tradable is False
    assert impact_bps == 10000 # Default high impact
