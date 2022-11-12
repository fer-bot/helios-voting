import os
from Crypto.Util import number

safeprimes = [
    298831631636265277171916710954079202878170290275988468156972461545617058014980437183653059579437554083000266030451712475795015306873686420415799327647627131282036835197823412013334476195886697253367478383864891034690734241627423496036950157953294123107137281730578086448691356900666823542043018049835336438387,
    256507429205034374206885864538956956659749914278949152186741723091816168909461523177193791543692902898871699802042461653361355567962619343625944395768599664950757312284809099400377521324478245218466598143970303331954215778359060716765025973343534630327003699570216493062332259174874195374478826042273646713527,
    135934744108442241983005018100380440442169071746142485205996146106410924700866734101197419324619098270601831171091285537613843956596362050115796344052042290479362583890437926121062380913222913896706416270932101187435466592539920816679815389233652473622380771019798309649416472390301527793461859629922208989919,
]


def generate_large_prime():
    n_length = int(os.getenv('CRYPTO_PRIME_LENGTH', 1024))
    p = number.getPrime(n_length)
    while not number.isPrime((p-1)//2):
        p = number.getPrime(n_length)
    return p