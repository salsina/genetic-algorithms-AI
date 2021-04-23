import random
testFile1 = "test1.txt"
testFile2 = "test2.txt"

def readInput(testFile) :
    file = open(testFile, 'r+')
    fileList = file.readlines()
    fileList = [s.replace('\n', '') for s in fileList]
    
    [days, doctors] = [int(i) for i in fileList[0].split()]
    maxCapacity = int(fileList[1])
    
    allShifts = []
    for i in range(2, days + 2):
        dayRequirements = fileList[i].split()
        morningReqs = [int(i) for i in dayRequirements[0].split(",")]
        eveningReqs = [int(i) for i in dayRequirements[1].split(",")]
        nightReqs = [int(i) for i in dayRequirements[2].split(",")]
        
        allShifts.append((morningReqs, eveningReqs, nightReqs))

    file.close()
    return [days, list(range(doctors)), maxCapacity, allShifts]


class JobScheduler:
    def __init__(self, fileInfo):
        self.days = fileInfo[0]
        self.doctors = len(fileInfo[1])
        self.doctorsIds = fileInfo[1]
        self.maxCapacity = fileInfo[2]
        self.allShifts = fileInfo[3]
        self.popSize = 300
        self.chromosomes = self.generateInitialPopulation()
        self.crossOverPoints = 3 * self.days 
        self.elitismPercentage = 0.16
        self.pc = 0.65
        self.pm = 0.4
        self.done = False
        
    def generateInitialPopulation(self):
        chromosomes = []
        for i in range(self.popSize):
            chromosome = []
            for day in self.allShifts:
                for shift in day:
                    num_of_doctors_in_shift = random.randint(0,self.doctors)
                    doctors_in_shift = ""
                    for j in range(num_of_doctors_in_shift):
                        doc_id = random.randint(0,self.doctors-1)
                        while str(doc_id) in doctors_in_shift:
                            doc_id = random.randint(0,self.doctors-1)
                        doctors_in_shift += str(doc_id) 
                    chromosome.append(doctors_in_shift)
            chromosomes.append(chromosome)
                        
        return chromosomes
        
    
    def crossOver(self, chromosome1, chromosome2):
        crossoverpoints = ""
        child1=[]
        child2=[]
        prev_index = 0
        chromo = 1
        for i in range(1,self.crossOverPoints):
            rand_num = random.random()
            if rand_num < self.pc:
                if(chromo == 1):
                    child1 += (chromosome1[prev_index:i])
                    child2 += (chromosome2[prev_index:i])
                    prev_index = i
                    chromo = 2
                else:
                    child1 += (chromosome2[prev_index:i])
                    child2 +=(chromosome1[prev_index:i])
                    prev_index = i
                    chromo = 1
        
        if(chromo == 1):
            child1 += (chromosome1[prev_index:])
            child2 += (chromosome2[prev_index:])
        else:
            child1 += (chromosome2[prev_index:])
            child2 +=(chromosome1[prev_index:])
            
        return child1,child2
        
    def mutate(self, chromosome):
        k = ""
        for i in range(self.crossOverPoints):
            rand_num = random.random()
            if rand_num < self.pm:
                gene = ""
                random_num_of_doctors = random.randint(0,self.doctors)
                for j in range(len(chromosome[i])):
                    doc_id = random.randint(0,self.doctors-1)
                    while str(doc_id) in gene:
                        doc_id = random.randint(0,self.doctors-1)
                    gene += str(doc_id)
                chromosome[i] = gene
        return chromosome
        
    def calculate_doctors_in_capacity(self,chromosome):
        doctors_days = [0] * self.doctors
        ok_doctors = 0
        for gene in chromosome:
            for doctor_id in gene:
                doctors_days[int(doctor_id)] += 1
                
        for i in doctors_days:
            if i <= self.maxCapacity:
                ok_doctors+=1
                
        return ok_doctors/self.doctors
    
    def calculate_doctors_3nights_shift(self,chromosome):
        doctors_days = [1] * self.doctors
        for i in range(2,len(chromosome)-6,3):
            for j in chromosome[i]:
                if doctors_days[int(j)] != 0:
                    if (j in chromosome[i+3]) and (j in chromosome[i+6]):
                        doctors_days[int(j)] = 0
        counter = 0
        for i in doctors_days:
            if i == 0:
                counter += 1
        return (self.doctors - counter)/self.doctors
    
    def calculate_doctors_tommorow_night_shift(self,chromosome):
        doctors_days = [1] * self.doctors
        for i in range(2,len(chromosome)-3,3):
            for j in chromosome[i]:
                if doctors_days[int(j)] != 0:
                    if (j in chromosome[i+1]) or (j in chromosome[i+2]):
                        doctors_days[int(j)] = 0
        counter = 0
        for i in doctors_days:
            if i == 0:
                counter += 1
        return (self.doctors - counter)/self.doctors

    def calculate_shift_limits(self,chromosome):
        ok_doctors = 0
        for day in range(len(self.allShifts)):
            for shift in range(len(self.allShifts[day])):
                min_doctors = self.allShifts[day][shift][0]
                max_doctors = self.allShifts[day][shift][1]
                doctors_in_shift = len(chromosome[day*3 + shift])
                if (doctors_in_shift >= min_doctors) and (doctors_in_shift <= max_doctors):
                    ok_doctors += 1
        
        return ok_doctors/len(chromosome)
    def caculateFitness(self, chromosome):
        doctors_in_shift_limit = self.calculate_shift_limits(chromosome)
        doctors_in_capacity = self.calculate_doctors_in_capacity(chromosome)
        doctors_3nights_shift = self.calculate_doctors_3nights_shift(chromosome)
        doctors_tommorow_night_shift = self.calculate_doctors_tommorow_night_shift(chromosome)
        return (5*doctors_in_shift_limit + doctors_in_capacity + doctors_3nights_shift + doctors_tommorow_night_shift)/8
    
    def put_default_best_chromosomes(self):
        self.chromosomes.sort(key = lambda x:self.caculateFitness(x))
        num = self.elitismPercentage * self.popSize
        if num - int(num) > 0:
            index = int(num) + 1
        else:
            index = int(num)
        highest = self.chromosomes[-index:]
        return highest,index
    
    def write_to_answer_file(self,ans_chromosome,filename):
        ans = ""
        c = 0
        # print(ans_chromosome)
        for gene in ans_chromosome:
            if gene == '':
                ans += 'empty,'
            for docId in gene:
                ans += docId + ','
            ans = ans[:-1]
            ans +=  ' '
            if c%3 == 2:
                ans = ans[:-1]
                ans += '\n'
            c += 1
        ans = ans[:-1]
        # print(ans)
        f = open(filename, "w")
        f.write(ans)
        f.close()
        
    def generateNewPopulation(self,filename):
        new_chromosomes,index = self.put_default_best_chromosomes()
        maximum_fitness = self.caculateFitness(new_chromosomes[-1])
        if maximum_fitness == 1:
            self.done = True
            ans_chromosome = new_chromosomes[-1]
            self.write_to_answer_file(ans_chromosome,filename)  
            return ans_chromosome
        # print(maximum_fitness)
        # print('....................................')
        
        for i in range(len(self.chromosomes)):
            chromosome1_index = random.randint(0,len(self.chromosomes)-1)
            chromosome2_index = random.randint(0,len(self.chromosomes)-1)
            while chromosome1_index == chromosome2_index:
                chromosome2_index = random.randint(0,len(self.chromosomes)-1)
                
            self.chromosomes[chromosome1_index], self.chromosomes[chromosome2_index] = \
                self.crossOver(self.chromosomes[chromosome1_index], self.chromosomes[chromosome2_index])
        
        for i in range(len(self.chromosomes)):
            chromosome1_index = random.randint(0,len(self.chromosomes)-1)
            self.chromosomes[chromosome1_index] = self.mutate(self.chromosomes[chromosome1_index])

        self.chromosomes.sort(key = lambda x:self.caculateFitness(x))
        self.chromosomes[:index] = new_chromosomes
        return self.chromosomes
    
    def schedule(self,filename): 
        while (not self.done):
            self.generateNewPopulation(filename)
    
import time

fileInfo1 = readInput(testFile1)

start = time.time()

scheduler = JobScheduler(fileInfo1)
scheduler.schedule("output1.txt")

end = time.time()

print("test 1: ", '%.2f'%(end - start), 'sec')

fileInfo2 = readInput(testFile2)

start = time.time()

scheduler = JobScheduler(fileInfo2)
scheduler.schedule("output2.txt")

end = time.time()

print("Test 2: ", '%.2f'%(end - start), 'sec')
