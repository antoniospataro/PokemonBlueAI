import sys
import subprocess
from Mover import Mover
from Pokemon import Move,Pokemon
import re

class LogicManager:
    
    def __init__(self):
        self.binList = list()
        self.empty = True
        self.binFileName = 'Dump.bin'
        self.myPokemonList = list()
        self.enemyPokemonList = list()
        self.moveList = list()
        self.typeList = list()
        self.mover = Mover()
        self.ai = AI()
        self.totEnemies=6
        self.oldposition=0
        
    def convertHex(self,hexValue):
        i = int(hexValue, 16)
        return i

    def createTypeList(self):
        file1 = open('type.info', 'r') 
        for line in file1: 
            print("{}".format(line.strip())) 
            self.typeList.append("{}".format(line.strip()))
        file1.close()

    def createMoveList(self):
        file1 = open('move.info', 'r') 
        for line in file1: 
            print("{}".format(line.strip())) 
            self.moveList.append("{}".format(line.strip()))
        file1.close()

    def convertBinary(self):
        if self.empty:
            outF = open("Dump.txt", "w")
        with open(self.binFileName, 'rb') as f1:
            A = f1.read()
            for addr in range(0x000,0xdfff+1):
                a = A[addr]
                if a!=0:
                    #print("{:04x}: {:04x}".format(addr,a))
                    if self.empty:
                        self.binList.append("{:04x} : {:04x}\n".format(addr,a))
                        outF.write("{:04x}: {:04x}\n".format(addr,a))
        if self.empty:
            outF.close()
            self.empty = False

    def clear(self):
        del self.binList
        del self.myPokemonList
        self.binList = list()
        self.myPokemonList = list()
        self.empty=True


    def matchMove(self,moveVal,line):
        matchObj = re.match(r'(\d+).+\s(\w+)\s+(physical|special|status).+\s(\d+\**)\s+(\d+|—)\s+(\d+%|—|\d+%\*)\s.*', line, re.M|re.I)
        move = Move()
        if matchObj is None:
            return None
        if moveVal == matchObj.group(1):
            move.type = matchObj.group(2)
            move.category = matchObj.group(3)
            if matchObj.group(5) != '—':
                move.power= matchObj.group(5)
            else:
                move.power = '0'
            return move
    
    def currentEnemy(self,actualEnemyAddr):
        opponent=0
        for data in self.binList:
            matchObj = re.match(r'(.+) : (.+)', data, re.M|re.I)
            if matchObj.group(1) == actualEnemyAddr: 
                opponent = str(self.convertHex(str(matchObj.group(2))))
        return  int(opponent)


    def setCurrentHp(self,hpAddr1,hpAddr2,poke):
        hp1 = 0
        hp2 = 0        
        for data in self.binList:
            matchObj = re.match(r'(.+) : (.+)', data, re.M|re.I)
            if matchObj.group(1) == hpAddr1: 
                hp1 = str(self.convertHex(str(matchObj.group(2))))
            if matchObj.group(1) == hpAddr2: 
                hp2 = str(self.convertHex(str(matchObj.group(2))))
        if hp1!=0 or hp2!=0:
            poke.hp = int(hp1)+int(hp2)
            print("CURRENT HP: " + str(int(hp1)+int(hp2)))


    
    def createPokemon(self,poke,hpAddr,type1Adrr,type2Addr,move1Addr,move2Addr,move3Addr,move4Addr):
        num = None
        hp = None
        moveVal1 = None
        moveVal2 = None
        moveVal3 = None
        moveVal4 = None
        typeVal1 = None
        typeVal2 = None
        
        #find all my data to match after in the correct list.info
        for data in self.binList:
            matchObj = re.match(r'(.+) : (.+)', data, re.M|re.I)
            if matchObj.group(1) == poke:
                num = str(self.convertHex(str(matchObj.group(2))))
                print("Pokemon N: "+num) 
            if matchObj.group(1) == hpAddr: 
                hp = str(self.convertHex(str(matchObj.group(2))))
                print("CURRENT HP: " + hp)
            if matchObj.group(1) == type1Adrr:
                typeVal1 = str(self.convertHex(str(matchObj.group(2))))
                print("TYPE 1 LIST NUMBER: " + typeVal1)
            if matchObj.group(1) == type2Addr: #in some cases is not present so i set type2 to 0
                typeVal2 = str(self.convertHex(str(matchObj.group(2))))
                print("TYPE 2 LIST NUMBER: " + typeVal2)
            if matchObj.group(1) == move1Addr:
                moveVal1 = str(self.convertHex(str(matchObj.group(2))))
                print("MOVE 1 LIST NUMBER: " + moveVal1)
            if matchObj.group(1) == move2Addr:           
                moveVal2 = str(self.convertHex(str(matchObj.group(2))))
                print("MOVE 2 LIST NUMBER: " + moveVal2)
            if matchObj.group(1) == move3Addr:           
                moveVal3 = str(self.convertHex(str(matchObj.group(2))))
                print("MOVE 3 LIST NUMBER: " + moveVal3)
            if matchObj.group(1) == move4Addr:           
                moveVal4 = str(self.convertHex(str(matchObj.group(2))))
                print("MOVE 4 LIST NUMBER: " + moveVal4)
            
        move1 = None
        move2 = None
        move3 = None
        move4 = None
        type1 = '0'
        type2 = '0'

        #Find all the 4 moves for my pokemon 
        for data in self.moveList:
            if self.matchMove(moveVal1,data) is not None:
                move1 = self.matchMove(moveVal1,data)
                print("MOVE 1: "+move1.category + move1.power+ move1.type)
            if self.matchMove(moveVal2,data) is not None:
                move2 = self.matchMove(moveVal2,data)
                print("MOVE 2: "+move2.category + move2.power+ move2.type)
            if self.matchMove(moveVal3,data) is not None:
                move3 = self.matchMove(moveVal3,data)
                print("MOVE 3: "+move3.category + move3.power+ move3.type)
            if self.matchMove(moveVal4,data) is not None:
                move4 = self.matchMove(moveVal4,data)
                print("MOVE 4: "+move4.category + move4.power + move4.type)
        #Find all the type 
        for data in self.typeList:
            matchObj = re.match(r'(\d+)\s+(\w+)\s+(\w+)', data, re.M|re.I)
            if matchObj.group(1) == typeVal1:
                type1 = matchObj.group(3)        
                print("N: "+typeVal1+" TYPE 1: "+matchObj.group(3))
            if typeVal2 != None:
                if matchObj.group(1) == typeVal2:
                    type2 = matchObj.group(3)         
                    print("N: "+typeVal2+" TYPE 2: "+matchObj.group(3))
        if typeVal2 == None:
            print("TYPE 2: " + type2)
        pokemon = Pokemon(num,hp,type1,type2,move1,move2,move3,move4)
        return pokemon    
    
    def start(self):
        self.createMoveList()
        self.createTypeList()
        self.mover.firstDump()
        self.convertBinary()
        print("ENEMY 1: ")
        self.enemyPokemonList.append(self.createPokemon('d8a4','d8a6','d8a9','d8aa','d8ac','d8ad','d8ae','d8af'))
        print("ENEMY 2: ")
        self.enemyPokemonList.append(self.createPokemon('d89e','d8d2','d8d5','d8d6','d8d8','d8d9','d8da','d8db'))
        print("ENEMY 3: ")
        self.enemyPokemonList.append(self.createPokemon('d8fc','d8fe','d901','d902','d904','d905','d906','d907'))
        print("ENEMY 4: ")
        self.enemyPokemonList.append(self.createPokemon('d828','d82a','d92d','d92e','d930','d931','d932','d933'))
        print("ENEMY 5: ")
        self.enemyPokemonList.append(self.createPokemon('d8a1','d856','d959','d95a','d95c','d95d','d95e','d95f'))
        print("ENEMY 6: ")
        self.enemyPokemonList.append(self.createPokemon('d8a1','d882','d985','d986','d988','d989','d98a','d98b'))
        while True:
            self.convertBinary()
            print("POKEMON 1: ")
            self.myPokemonList.append(self.createPokemon('d164','d16d','d170','d171','d01c','d01d','d01e','d01f'))
            print("POKEMON 2: ")
            self.myPokemonList.append(self.createPokemon('d165','d199','d19c','d19d','d19f','d1a0','d1a1','d1a2'))
            print("POKEMON 3: ")
            self.myPokemonList.append(self.createPokemon('d166','d1c5','d1c8','d1c9','d1cb','d1cc','d1cd','d1ce'))
            print("POKEMON 4: ")
            self.myPokemonList.append(self.createPokemon('d167','d1f1','d1f4','d1f5','d1f7','d1f8','d1f9','d1fa'))
            print("POKEMON 5: ")
            self.myPokemonList.append(self.createPokemon('d168','d21d','d220','d221','d223','d224','d225','d226'))
            print("POKEMON 6: ")
            self.myPokemonList.append(self.createPokemon('d169','d249','d24c','d24d','d24f','d250','d251','d252'))        
            print("CURRENT ENEMY NUMBER: " + str(self.currentEnemy('cfe5')))
            currEnmIndex=0
            for poke in range(0,len(self.enemyPokemonList)):
                if self.enemyPokemonList[poke].number == str(self.currentEnemy('cfe5')):
                    print("FOUND IN ENEMY LIST!")
                    currEnmIndex = poke
            print("HP Current ENEMY: ")
            self.setCurrentHp('cfe7','cfe8',self.enemyPokemonList[currEnmIndex])
            moveVal = int(self.ai.dlvBattleAI(self.myPokemonList[0],self.enemyPokemonList[currEnmIndex]))
            if moveVal > self.oldposition:
                self.mover.pressMoveX(moveVal-self.oldposition)
            else:
                self.mover.pressMoveX(self.oldposition-moveVal)
            self.clear()
            self.oldposition=moveVal
    
class AI:
    
    def __init__(self):
        self.roundConst= 'roundConst.dlv'
        self.round='round.dlv'
        self.changePokemonConst= 'changeConst.dlv'
        self.changePokemon = 'changePokemon.dlv'
        self.fact = list()
        self.roundListProgram = list()
        self.createRoundList()
    
    def matchSolution(self):
        pass 

    def createRoundList(self):
        file1 = open(self.roundConst, 'r') 
        for line in file1: 
            print("{}".format(line.strip())) 
            self.roundListProgram.append("{}".format(line.strip()))
        file1.close()

    def createFactList(self, myPokemon, enemyPokemon):
        print("INSERT FACTS")
        self.fact.append(f"plMvType(1,{myPokemon.move1.type},{myPokemon.move1.power}). ")
        self.fact.append(f"plMvType(2,{myPokemon.move2.type},{myPokemon.move2.power}). ")
        self.fact.append(f"plMvType(3,{myPokemon.move3.type},{myPokemon.move3.power}). ")
        self.fact.append(f"plMvType(4,{myPokemon.move4.type},{myPokemon.move4.power}). ")
        self.fact.append(f"plType({myPokemon.type1}). ")
        self.fact.append(f"plType({myPokemon.type2}). ")
        self.fact.append(f"enmType({enemyPokemon.type1}). ")
        self.fact.append(f"enmType({enemyPokemon.type2}). ")
        self.fact.append(f"HP({myPokemon.hp}). ")        

    def dlvBattleAI(self,myPokemon,enemyPokemon):
        self.createFactList(myPokemon,enemyPokemon)
        outF = open(self.round, "w")
        for line in self.fact:
            outF.write(f"{line}")
        for line in self.roundListProgram:
            outF.write(f"{line}\n")
        outF.close()
        string=f"./dlv2 {self.round} --no-fact"
        result=subprocess.getoutput(string)
        l=result.split(', ')
        l[0]=l[0].replace('DLV 2.0\n\n{', '')
        value=0
        print(l)
        for data in l:
            #\w+\((\d).*
            matchObj = re.match(r'choiceMv\((\d).*', data, re.M|re.I)
            if matchObj is not None:
                print("MOVE: "+matchObj.group())
                return matchObj.group(1) 



man = LogicManager()
#man.convertBinary()
man.start()
