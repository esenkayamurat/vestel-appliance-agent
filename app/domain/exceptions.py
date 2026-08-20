class DomainError(Exception):
    """Tum domain-seviyesi hatalarin ortak atasi."""


class UnsupportedQueryError(DomainError):
    """Agent, kullanicinin sorusunu elindeki tool'larla cevaplayamadiginda firlatilir."""
