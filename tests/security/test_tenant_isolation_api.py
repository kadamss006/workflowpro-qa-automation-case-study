import pytest


@pytest.mark.security
@pytest.mark.parametrize("spoofed_tenant", ["company2", "unknown", "", "COMPANY1"])
def test_tenant_header_cannot_override_token_scope(api_context, company1_token, spoofed_tenant):
    response = api_context.get(
        "/api/v1/projects",
        headers={
            "Authorization": f"Bearer {company1_token}",
            "X-Tenant-ID": spoofed_tenant,
        },
    )
    assert response.status in {400, 403, 404}
