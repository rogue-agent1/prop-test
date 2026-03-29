#!/usr/bin/env python3
"""prop_test - Property-based testing with random data generators."""
import sys, random, string

def integers(lo=-1000, hi=1000):
    return lambda: random.randint(lo, hi)

def floats(lo=-1000.0, hi=1000.0):
    return lambda: random.uniform(lo, hi)

def strings(min_len=0, max_len=50, charset=None):
    chars = charset or string.ascii_letters + string.digits
    return lambda: "".join(random.choice(chars) for _ in range(random.randint(min_len, max_len)))

def lists(gen, min_len=0, max_len=20):
    return lambda: [gen() for _ in range(random.randint(min_len, max_len))]

def one_of(*gens):
    return lambda: random.choice(gens)()

def check(prop, gens, trials=100, seed=None):
    if seed is not None: random.seed(seed)
    for i in range(trials):
        args = [g() for g in gens]
        try:
            result = prop(*args)
            if result is False:
                return {"status": "fail", "trial": i, "args": args}
        except Exception as e:
            return {"status": "error", "trial": i, "args": args, "error": str(e)}
    return {"status": "pass", "trials": trials}

def test():
    # Addition is commutative
    r = check(lambda a, b: a + b == b + a, [integers(), integers()], trials=200, seed=42)
    assert r["status"] == "pass"
    # Sorting is idempotent
    r2 = check(lambda xs: sorted(sorted(xs)) == sorted(xs), [lists(integers())], seed=42)
    assert r2["status"] == "pass"
    # Reverse of reverse is identity
    r3 = check(lambda xs: list(reversed(list(reversed(xs)))) == xs, [lists(integers())], seed=42)
    assert r3["status"] == "pass"
    # Deliberate failure
    r4 = check(lambda x: x < 500, [integers(0, 1000)], trials=1000, seed=42)
    assert r4["status"] == "fail"
    print("prop_test: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: prop_test.py --test")
