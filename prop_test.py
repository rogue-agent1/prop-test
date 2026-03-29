#!/usr/bin/env python3
"""Property-based testing framework."""
import random, traceback

class Arbitrary:
    @staticmethod
    def int(min_val=-1000, max_val=1000):
        return lambda: random.randint(min_val, max_val)
    @staticmethod
    def string(max_len=20):
        return lambda: ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(random.randint(0, max_len)))
    @staticmethod
    def list_of(gen, max_len=10):
        return lambda: [gen() for _ in range(random.randint(0, max_len))]
    @staticmethod
    def bool():
        return lambda: random.choice([True, False])
    @staticmethod
    def float(min_val=-1000, max_val=1000):
        return lambda: random.uniform(min_val, max_val)

def forall(*generators, trials=100):
    def decorator(fn):
        def wrapper():
            for trial in range(trials):
                args = [g() for g in generators]
                try:
                    result = fn(*args)
                    if result is False:
                        return {"status": "FAIL", "trial": trial, "args": args}
                except Exception as e:
                    return {"status": "ERROR", "trial": trial, "args": args, "error": str(e)}
            return {"status": "PASS", "trials": trials}
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

def check(prop, verbose=False):
    result = prop()
    if verbose or result["status"] != "PASS":
        print(f"  {prop.__name__}: {result['status']}", end="")
        if result["status"] != "PASS":
            print(f" at trial {result['trial']} with args={result['args']}", end="")
            if "error" in result:
                print(f" error={result['error']}", end="")
        print()
    return result["status"] == "PASS"

if __name__ == "__main__":
    @forall(Arbitrary.list_of(Arbitrary.int()))
    def sort_preserves_length(xs):
        return len(sorted(xs)) == len(xs)
    check(sort_preserves_length, verbose=True)

def test():
    random.seed(42)
    @forall(Arbitrary.int(), Arbitrary.int(), trials=50)
    def commutative_add(a, b):
        return a + b == b + a
    assert check(commutative_add)
    @forall(Arbitrary.list_of(Arbitrary.int()), trials=50)
    def sort_idempotent(xs):
        return sorted(sorted(xs)) == sorted(xs)
    assert check(sort_idempotent)
    @forall(Arbitrary.string(), trials=50)
    def reverse_reverse(s):
        return s[::-1][::-1] == s
    assert check(reverse_reverse)
    # Failing property
    @forall(Arbitrary.int(1, 100), trials=50)
    def always_even(n):
        return n % 2 == 0
    result = always_even()
    assert result["status"] == "FAIL"
    print("  prop_test: ALL TESTS PASSED")
