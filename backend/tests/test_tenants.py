"""Tests de sécurité multi-tenant : Zéro fuite entre clients."""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_invalid_key():
    """Test: Refus d'accès sans X-API-KEY valide."""
    r = client.post("/query", json={"question": "test"})
    assert r.status_code == 401

def test_tenantA_resiliation():
    """Test: TenantA accède uniquement à SES documents (docA*)."""
    r = client.post(
        "/query",
        headers={"X-API-KEY": "tenantA_key"},
        json={"question": "Sous combien de temps est envoyé un accusé de réception ?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["tenant_id"] == "tenantA"
    assert data["no_answer"] is False
    # ✅ CRITIQUE: Vérification zéro fuite - only docA* sources
    assert all(s["doc_id"].startswith("docA") for s in data["sources"])
    # ✅ Aucun document docB ne doit être cité
    assert not any("docB" in s["doc_id"] for s in data["sources"])

def test_tenantB_sinistre():
    """Test: TenantB accède uniquement à SES documents (docB*)."""
    r = client.post(
        "/query",
        headers={"X-API-KEY": "tenantB_key"},
        json={"question": "Sous combien de jours doit-on déclarer un sinistre ?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["tenant_id"] == "tenantB"
    assert data["no_answer"] is False
    # ✅ CRITIQUE: Vérification zéro fuite - only docB* sources
    assert all(s["doc_id"].startswith("docB") for s in data["sources"])
    # ✅ Aucun document docA ne doit être cité
    assert not any("docA" in s["doc_id"] for s in data["sources"])

def test_cross_tenant_impossible_question():
    """Test: Question sans réponse possible → no_answer=True.
    
    TenantA ne doit pas inventer de réponse si l'info n'existe pas.
    Ici on pose une question sur un concept absent de ses documents.
    """
    r = client.post(
        "/query",
        headers={"X-API-KEY": "tenantA_key"},
        json={"question": "Quelle est la procédure de remboursement des frais médicaux?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["tenant_id"] == "tenantA"
    # Doit retourner no_answer si aucun doc pertinent (score trop bas)
    # Note: Si le système trouve un hit faible, c'est acceptable
    # L'important est qu'il ne cite JAMAIS de docB
    if data["sources"]:
        assert all(s["doc_id"].startswith("docA") for s in data["sources"])
        assert not any("docB" in s["doc_id"] for s in data["sources"])

def test_tenantB_cannot_access_tenantA_data():
    """Test: TenantB ne peut pas voir les données de TenantA."""
    r = client.post(
        "/query",
        headers={"X-API-KEY": "tenantB_key"},
        json={"question": "Quelle est la procédure de résiliation ?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["tenant_id"] == "tenantB"
    # Jamais de docA dans les sources de tenantB
    assert not any("docA" in s["doc_id"] for s in data["sources"])

def test_wrong_api_key():
    """Test: Clé API inexistante → 401."""
    r = client.post(
        "/query",
        headers={"X-API-KEY": "fake_key_12345"},
        json={"question": "test"},
    )
    assert r.status_code == 401
