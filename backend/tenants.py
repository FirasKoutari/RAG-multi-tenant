from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Tenant:
    id: str
    api_key: str

# 🔒 CONFIGURATION MULTI-TENANT
# --------------------------------
# En production, stocker les clés dans:
# - Variables d'environnement
# - Secret manager (AWS Secrets, Azure Key Vault, etc.)
# - Base de données sécurisée
#
# Pour le test technique, dictionnaire en dur acceptable.
TENANTS = {
    "tenantA_key": Tenant(id="tenantA", api_key="tenantA_key"),
    "tenantB_key": Tenant(id="tenantB", api_key="tenantB_key"),
}

def resolve_tenant(api_key: str | None) -> Tenant | None:
    """Résout un tenant depuis sa clé API.
    
    🔑 Point d'entrée de l'authentification multi-tenant.
    Retourne None si la clé est invalide/absente.
    """
    if not api_key:
        return None
    return TENANTS.get(api_key)
