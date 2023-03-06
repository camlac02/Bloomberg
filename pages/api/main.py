import sys
import random


def fun():
    x = 20
    return f'{str(sys.argv[1])} + {random.randint(3, 15)}'


print(
    f"Si tu vois cette ligne chaco, elle provient de Python, ici tu rajoute ton mot : {sys.argv[1]} de grand {sys.argv[2]}, ici on a une fonction qui renvoi le mot que tu a ecris et qui rajoute un nombre au hasard entre 3 et 15 a la fin : {fun()}, le code python est renvoye a une API local qu'ont lis depuis notre frontend sans avoir de serveur a gerer, du serverless node + python")
