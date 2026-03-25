def vec(a, b):
    return (b[0] - a[0], b[1] - a[1])

def dot(a, b):
    return a[0]*b[0] + a[1]*b[1]

def length(v):
    return (v[0]**2 + v[1]**2) ** 0.5