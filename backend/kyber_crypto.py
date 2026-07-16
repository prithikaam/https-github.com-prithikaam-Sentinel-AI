import random
import hashlib
import numpy as np

# CRYSTALS-Kyber Parameters (Kyber-512 parameters)
N = 256
Q = 3329
ETA = 2  # Noise parameter

class Polynomial:
    def __init__(self, coeffs=None):
        if coeffs is None:
            self.coeffs = [0] * N
        else:
            # Ensure exactly N coefficients
            self.coeffs = [int(c) % Q for c in coeffs]
            if len(self.coeffs) < N:
                self.coeffs += [0] * (N - len(self.coeffs))
            elif len(self.coeffs) > N:
                self.coeffs = self.coeffs[:N]

    def __add__(self, other):
        res = [(self.coeffs[i] + other.coeffs[i]) % Q for i in range(N)]
        return Polynomial(res)

    def __sub__(self, other):
        res = [(self.coeffs[i] - other.coeffs[i]) % Q for i in range(N)]
        return Polynomial(res)

    def __mul__(self, other):
        # Negacyclic convolution modulo X^N + 1
        res = [0] * (2 * N)
        for i in range(N):
            for j in range(N):
                res[i + j] = (res[i + j] + self.coeffs[i] * other.coeffs[j]) % Q
        
        # Reduce modulo X^N + 1 (i.e., X^N = -1)
        final_coeffs = [0] * N
        for i in range(N):
            final_coeffs[i] = (res[i] - res[i + N]) % Q
        return Polynomial(final_coeffs)

    def to_hex(self):
        # Package coefficients into a byte string and return hex
        byte_data = bytearray()
        for c in self.coeffs:
            # Represent each 12-bit coeff (since Q=3329) as 2 bytes
            byte_data.append(c & 0xFF)
            byte_data.append((c >> 8) & 0xFF)
        return byte_data.hex()

    @staticmethod
    def from_hex(hex_str):
        byte_data = bytes.fromhex(hex_str)
        coeffs = []
        for i in range(0, len(byte_data), 2):
            if i + 1 < len(byte_data):
                val = byte_data[i] + (byte_data[i+1] << 8)
                coeffs.append(val)
        return Polynomial(coeffs)

def cbd(eta):
    """Centered Binomial Distribution sampling for error polynomials"""
    coeffs = []
    for _ in range(N):
        # Generate 2*eta random bits
        a = sum(random.randint(0, 1) for _ in range(eta))
        b = sum(random.randint(0, 1) for _ in range(eta))
        coeffs.append((a - b) % Q)
    return Polynomial(coeffs)

def generate_random_poly():
    """Generates a random uniform polynomial in R_q"""
    coeffs = [random.randint(0, Q - 1) for _ in range(N)]
    return Polynomial(coeffs)

# Kyber-512 KEM Operations
def generate_keypair():
    """
    Kyber Key Generation
    Returns:
        pk (dict): Public key containing public matrix element A and vector t.
        sk (dict): Secret key containing s.
        trace (dict): Step-by-step debug information.
    """
    # A is a 2x2 matrix of polynomials (Kyber-512 has k=2 modules)
    # For simplified simulation, let's use k=2 dimensions
    A = [
        [generate_random_poly(), generate_random_poly()],
        [generate_random_poly(), generate_random_poly()]
    ]
    
    # Secret key s (2-vector of noise polynomials)
    s = [cbd(ETA), cbd(ETA)]
    
    # Error vector e (2-vector of noise polynomials)
    e = [cbd(ETA), cbd(ETA)]
    
    # t = A * s + e
    # t[0] = A[0][0]*s[0] + A[0][1]*s[1] + e[0]
    # t[1] = A[1][0]*s[0] + A[1][1]*s[1] + e[1]
    t0 = A[0][0] * s[0] + A[0][1] * s[1] + e[0]
    t1 = A[1][0] * s[0] + A[1][1] * s[1] + e[1]
    
    trace = {
        "step": "Key Generation",
        "A_matrix": [[p.to_hex()[:16] + "..." for p in row] for row in A],
        "secret_s": [p.to_hex()[:16] + "..." for p in s],
        "error_e": [p.to_hex()[:16] + "..." for p in e],
        "t_vector": [t0.to_hex()[:16] + "...", t1.to_hex()[:16] + "..."]
    }
    
    pk = {
        "A": [[p.to_hex() for p in row] for row in A],
        "t": [t0.to_hex(), t1.to_hex()]
    }
    
    sk = {
        "s": [p.to_hex() for p in s]
    }
    
    return pk, sk, trace

def encode_msg(msg_bytes):
    """Encode a 32-byte message into a polynomial (coefficients are 0 or Q/2)"""
    coeffs = [0] * N
    for i in range(len(msg_bytes)):
        b = msg_bytes[i]
        for j in range(8):
            bit = (b >> j) & 1
            coeffs[i * 8 + j] = bit * (Q // 2)
    return Polynomial(coeffs)

def decode_poly(poly):
    """Decode a polynomial back into a 32-byte message"""
    msg_bytes = bytearray(32)
    for i in range(32):
        b = 0
        for j in range(8):
            coeff = poly.coeffs[i * 8 + j]
            # If closer to Q/2 than 0 or Q, it is 1
            diff_q2 = abs(coeff - Q // 2)
            diff_0 = min(coeff, Q - coeff)
            bit = 1 if diff_q2 < diff_0 else 0
            b |= (bit << j)
        msg_bytes[i] = b
    return bytes(msg_bytes)

def encapsulate(pk):
    """
    Kyber Encapsulation
    Args:
        pk (dict): Public key.
    Returns:
        c (dict): Ciphertext.
        ss (str): Hex-encoded 256-bit Shared Secret.
        trace (dict): Step-by-step debug information.
    """
    A = [[Polynomial.from_hex(hex_str) for hex_str in row] for row in pk["A"]]
    t = [Polynomial.from_hex(hex_str) for hex_str in pk["t"]]
    
    # 1. Random 32-byte message
    msg = bytearray(random.getrandbits(8) for _ in range(32))
    
    # 2. Encode message to polynomial
    m_poly = encode_msg(msg)
    
    # 3. Noise vector r
    r = [cbd(ETA), cbd(ETA)]
    
    # 4. Error vectors e1 (vector of 2) and e2 (single poly)
    e1 = [cbd(ETA), cbd(ETA)]
    e2 = cbd(ETA)
    
    # 5. u = A^T * r + e1
    # u[0] = A[0][0]*r[0] + A[1][0]*r[1] + e1[0]
    # u[1] = A[0][1]*r[0] + A[1][1]*r[1] + e1[1]
    u0 = A[0][0] * r[0] + A[1][0] * r[1] + e1[0]
    u1 = A[0][1] * r[0] + A[1][1] * r[1] + e1[1]
    
    # 6. v = t^T * r + e2 + m_poly
    v = t[0] * r[0] + t[1] * r[1] + e2 + m_poly
    
    ciphertext = {
        "u": [u0.to_hex(), u1.to_hex()],
        "v": v.to_hex()
    }
    
    # 7. Hash the message and ciphertext to generate Shared Secret
    c_bytes = (u0.to_hex() + u1.to_hex() + v.to_hex()).encode('utf-8')
    ss = hashlib.sha256(msg + c_bytes).hexdigest()
    
    trace = {
        "step": "Encapsulation",
        "random_message_hex": msg.hex(),
        "encoded_msg_poly": m_poly.to_hex()[:16] + "...",
        "r_vector": [p.to_hex()[:16] + "..." for p in r],
        "u_vector": [u0.to_hex()[:16] + "...", u1.to_hex()[:16] + "..."],
        "v_poly": v.to_hex()[:16] + "...",
        "shared_secret": ss
    }
    
    return ciphertext, ss, trace

def decapsulate(ciphertext, sk, pk):
    """
    Kyber Decapsulation
    Args:
        ciphertext (dict): Ciphertext (u, v).
        sk (dict): Secret key (s).
        pk (dict): Public key (needed for verifying key agreement hash).
    Returns:
        ss (str): Decapsulated shared secret.
        trace (dict): Step-by-step debug information.
    """
    u = [Polynomial.from_hex(hex_str) for hex_str in ciphertext["u"]]
    v = Polynomial.from_hex(ciphertext["v"])
    s = [Polynomial.from_hex(hex_str) for hex_str in sk["s"]]
    
    # 1. Recover polynomial m_poly = v - s^T * u
    # s^T * u = s[0]*u[0] + s[1]*u[1]
    su = s[0] * u[0] + s[1] * u[1]
    m_recovered_poly = v - su
    
    # 2. Decode message
    msg = decode_poly(m_recovered_poly)
    
    # 3. Hash to get Shared Secret
    c_bytes = (ciphertext["u"][0] + ciphertext["u"][1] + ciphertext["v"]).encode('utf-8')
    ss = hashlib.sha256(msg + c_bytes).hexdigest()
    
    trace = {
        "step": "Decapsulation",
        "recovered_message_hex": msg.hex(),
        "decrypted_msg_poly": m_recovered_poly.to_hex()[:16] + "...",
        "shared_secret": ss
    }
    
    return ss, trace

if __name__ == "__main__":
    # Self-test Kyber KEM
    print("Testing Crystals-Kyber Simulation...")
    pk, sk, g_trace = generate_keypair()
    print("Keypair generated successfully.")
    
    c, ss_enc, e_trace = encapsulate(pk)
    print("Encapsulation completed. Shared Secret:", ss_enc)
    
    ss_dec, d_trace = decapsulate(c, sk, pk)
    print("Decapsulation completed. Shared Secret:", ss_dec)
    
    assert ss_enc == ss_dec, "Error! Shared secrets do not match."
    print("Kyber Verification SUCCESSFUL! Shared secrets match.")
