from coins.models import CoinTransaction


def award_normativ_coins(student, normativ, score, created_by):
    if score is None or score <= 0:
        return None

    marker = f'normativ:{normativ.pk}'
    exists = CoinTransaction.objects.filter(
        student=student,
        reason=CoinTransaction.Reason.NORMATIV,
        comment__contains=marker,
    ).exists()
    if exists:
        return None

    return CoinTransaction.objects.create(
        student=student,
        amount=score,
        reason=CoinTransaction.Reason.NORMATIV,
        comment=f'{marker} | {normativ.title}',
        created_by=created_by,
    )
