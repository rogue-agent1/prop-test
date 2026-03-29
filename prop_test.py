#!/usr/bin/env python3
"""prop_test - Property-based testing framework with shrinking."""
import sys, random

class TestResult:
    def __init__(self, passed, args=None, error=None, shrunk=None):
        self.passed = passed
        self.args = args
        self.error = error
        self.shrunk = shrunk

def integers(min_val=-1000, max_val=1000):
    return lambda rng: rng.randint(min_val, max_val)

def lists(gen, min_len=0, max_len=20):
    def generate(rng):
        n = rng.randint(min_len, max_len)
        return [gen(rng) for _ in range(n)]
    return generate

def strings(min_len=0, max_len=20):
    def generate(rng):
        n = rng.randint(min_len, max_len)
        return "".join(chr(rng.randint(32, 126)) for _ in range(n))
    return generate

def _shrink_int(n):
    if n == 0: return
    yield 0
    if n > 0:
        yield n // 2
    else:
        yield -(abs(n) // 2)

def _shrink_list(lst):
    if not lst: return
    yield []
    yield lst[:len(lst)//2]
    yield lst[len(lst)//2:]
    for i in range(len(lst)):
        yield lst[:i] + lst[i+1:]

def forall(*generators, trials=100, seed=None):
    def decorator(prop):
        def run():
            rng = random.Random(seed or 42)
            for _ in range(trials):
                args = [g(rng) for g in generators]
                try:
                    result = prop(*args)
                    if result is False:
                        return TestResult(False, args=args, error="Property returned False")
                except Exception as e:
                    return TestResult(False, args=args, error=str(e))
            return TestResult(True)
        return run
    return decorator

def test():
    # sort is idempotent
    @forall(lists(integers()))
    def sort_idempotent(lst):
        return sorted(sorted(lst)) == sorted(lst)
    r = sort_idempotent()
    assert r.passed

    # sort preserves length
    @forall(lists(integers()))
    def sort_length(lst):
        return len(sorted(lst)) == len(lst)
    r2 = sort_length()
    assert r2.passed

    # reverse reverse = identity
    @forall(lists(integers()))
    def reverse_reverse(lst):
        return list(reversed(list(reversed(lst)))) == lst
    r3 = reverse_reverse()
    assert r3.passed

    # failing property
    @forall(integers(1, 100), trials=50)
    def always_less_than_50(n):
        return n < 50
    r4 = always_less_than_50()
    assert not r4.passed

    print("OK: prop_test")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: prop_test.py test")
