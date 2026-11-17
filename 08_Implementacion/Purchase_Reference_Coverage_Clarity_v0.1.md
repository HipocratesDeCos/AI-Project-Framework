# Purchase reference coverage clarity v0.1

Ribbon coverage is floored for display only; STK values retain their precision.
The synthesis shows applicable reference coverage even when finance parameters
or an acknowledged purchase stock scenario are missing. REFERENCE_ONLY never
asserts that the proposed quantity meets its target. The snapshot preserves this
explanation. No old saved study is recalculated.

The ribbon displays article family next to article identity. New saved studies
capture family; old studies display missing family without consulting today's
catalogue.

A FINANCE_PARAMETERS blocking code explains why no cash-checked alternatives can
be calculated and provides a direct configuration action. Neither the imported
workbook nor this UI change activates a treasury reserve or horizon implicitly.
Browser regression expectations include fractional-day flooring and family.
Backend regressions cover stock reference survival before finance activation.
