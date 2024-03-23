from string import ascii_letters
from srec.compiler import RDCompiler

identifier_pattern = f"[{ascii_letters + '_'}].*"
text = "My_Var1"

atm = RDCompiler().compile(identifier_pattern)
print(atm.match(text))
