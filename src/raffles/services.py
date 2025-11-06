from __future__ import annotations

import random
from typing import Iterable

from django.db import IntegrityError

from .models import Raffle, RaffleTicketAllocation


class RaffleSoldOutError(Exception):
    """Raised when the raffle has no numbers available for allocation."""


def pick_random_numbers(raffle: Raffle, quantity: int) -> list[int]:
    """
    Selects random available numbers for the raffle.

    Mantém a solução simples por enquanto, suficiente para MVP. Confiamos
    na constraint de unicidade da model para segurar concorrência; em caso de
    colisão alguém reprocessa a operação.
    """
    if quantity <= 0:
        return []

    available = list(iter_available_numbers(raffle))
    if len(available) < quantity:
        raise RaffleSoldOutError("Não há números suficientes disponíveis para esta rifa.")

    return random.sample(available, quantity)


def iter_available_numbers(raffle: Raffle) -> Iterable[int]:
    allocated = set(
        raffle.ticket_allocations.values_list("number", flat=True)
    )
    for number in range(1, raffle.total_numbers + 1):
        if number not in allocated:
            yield number


def safe_allocate_number(**kwargs) -> RaffleTicketAllocation:
    """Helper para tentar criar uma alocação e repetir em caso de colisão."""
    for _ in range(3):
        try:
            return RaffleTicketAllocation.objects.create(**kwargs)
        except IntegrityError:
            continue
    raise

