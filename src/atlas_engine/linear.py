"""Small exact linear-system solver shared by independent model formulations."""

from fractions import Fraction


def solve_linear(
    coefficients: list[list[Fraction]], constants: list[Fraction]
) -> list[Fraction]:
    """Solve a square nonsingular system by exact Gauss-Jordan elimination."""
    size = len(coefficients)
    if size == 0 or len(constants) != size or any(len(row) != size for row in coefficients):
        raise ValueError("expected a nonempty square linear system")

    augmented = [list(row) + [constants[index]] for index, row in enumerate(coefficients)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column]), None)
        if pivot is None:
            raise ValueError("linear system is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]

        divisor = augmented[column][column]
        augmented[column] = [entry / divisor for entry in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = augmented[row][column]
            if multiplier:
                augmented[row] = [
                    current - multiplier * pivot_entry
                    for current, pivot_entry in zip(augmented[row], augmented[column], strict=True)
                ]
    return [augmented[row][-1] for row in range(size)]

