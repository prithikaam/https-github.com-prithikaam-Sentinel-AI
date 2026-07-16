import kyber_crypto

def test_kyber_kem():
    print("==================================================")
    print("Testing CRYSTALS-Kyber-512 KEM Simulation")
    print("==================================================")
    
    # 1. Key generation
    print("[1] Executing Key Generation...")
    pk, sk, keygen_trace = kyber_crypto.generate_keypair()
    print("Public Key (pk) vector t dimensions:", len(pk["t"]))
    print("Secret Key (sk) s dimensions:", len(sk["s"]))
    
    # 2. Encapsulation
    print("[2] Executing Encapsulation (Server -> Client)...")
    ciphertext, ss_enc, encaps_trace = kyber_crypto.encapsulate(pk)
    print("Ciphertext c u-vector size:", len(ciphertext["u"]))
    print("Shared Secret Encapsulated:", ss_enc)
    
    # 3. Decapsulation
    print("[3] Executing Decapsulation (Client -> Server)...")
    ss_dec, decaps_trace = kyber_crypto.decapsulate(ciphertext, sk, pk)
    print("Shared Secret Decapsulated:", ss_dec)
    
    # 4. Check matching secret
    assert ss_enc == ss_dec, "ERROR: Shared secrets do not match!"
    print("\n[SUCCESS] Kyber KEM verified. Secrets match perfectly.")
    print("==================================================")

if __name__ == "__main__":
    test_kyber_kem()
