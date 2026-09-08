"""Generic exact rational linear algebra shared by separate constructions."""

from __future__ import annotations

from fractions import Fraction


Matrix = list[list[Fraction]]
Vector = list[Fraction]


def identity(size: int) -> Matrix:
    return [[Fraction(row == column) for column in range(size)] for row in range(size)]


def minor(matrix: Matrix, row: int, column: int) -> Matrix:
    return [values[:column] + values[column + 1 :] for i, values in enumerate(matrix) if i != row]


def determinant(matrix: Matrix) -> Fraction:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    if size == 0:
        return Fraction(1)
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result *= -1
        pivot_value = work[column][column]
        result *= pivot_value
        for entry in range(column, size):
            work[column][entry] /= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column]
            if factor:
                for entry in range(column, size):
                    work[row][entry] -= factor * work[column][entry]
    return result


def rank(matrix: Matrix) -> int:
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("rank requires a rectangular matrix")
    work = [row[:] for row in matrix]
    pivot_row = 0
    for column in range(width):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        for entry in range(column, width):
            work[pivot_row][entry] /= pivot_value
        for row in range(len(work)):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                for entry in range(column, width):
                    work[row][entry] -= factor * work[pivot_row][entry]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def solve(coefficients: Matrix, constants: Vector) -> Vector:
    size = len(coefficients)
    if len(constants) != size or any(len(row) != size for row in coefficients):
        raise ValueError("solve requires a square system")
    if size == 0:
        return []
    augmented = [coefficients[i][:] + [constants[i]] for i in range(size)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column]), None)
        if pivot is None:
            raise ValueError("linear system is singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    augmented[row][entry] - factor * augmented[column][entry]
                    for entry in range(size + 1)
                ]
    return [augmented[row][-1] for row in range(size)]


def matrix_vector(matrix: Matrix, vector: Vector) -> Vector:
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("incompatible matrix and vector")
    return [sum((entry * value for entry, value in zip(row, vector, strict=True)), Fraction(0)) for row in matrix]
