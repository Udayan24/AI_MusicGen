# Import dependencies | Size: 210, 389
import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow
import screen4
from pyo import *
from typing import List, Dict
from random import choices
from midiutil import MIDIFile

from GA import selection_pair, single_point_crossover, mutation

from threading import Timer

import time
bits_per_note=4

# Setup UI
ui = screen4.Ui_MainWindow()
app = QApplication([])
win=QMainWindow()

ui.setupUi(win)

# -------------------------------------------
def eventGen(genome, bars, N_notes, steps, key, scale, root, bbpm):
    melody = melodyGen(genome, bars, N_notes, steps, key, scale, root)
    print("\nGenome:", genome)
    print("Bars:", bars)
    print("Notes:", N_notes)
    print("Key:", key)
    print("Scale:", scale)
    print("Root:", root)
    print("Notesss: ", melody['notes'])
    print("BPM: ", bbpm)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            attack=0.001,
            decay=0.05,
            sustain=3,
            release=0.005,
            bpm=bbpm
        ) for step in melody["notes"]
    ]

# --------------------------------------------------------------------------------
def intGen(bits: List[int]) -> int:
    return int(sum([bit*pow(2,index) for index, bit in enumerate(bits)]))

def melodyGen(genome, bars, N_notes, n_steps, key, scale, root) -> Dict[str, list]:
    notes = [genome[i:i+bits_per_note] for i in range(N_notes*bars)]
    print("Notes:", notes)

    # 1 bar => 4 notes.
    note_length = 4 / float(N_notes)

    #       Construct a list of pitches according to arguments
    scl = EventScale(root=key, scale=scale, first=root)

    #       Melody is represented by a dictionary. 
    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    for note in notes:
        integer = intGen(note)

        if integer >= pow(2, bits_per_note-1):
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]
    
    print("-----------------------")
    print("Notes:", melody['notes'])

    steps = []
    for step in range(n_steps):
        steps.append([scl[(note+step*2) % len(scl)] for note in melody["notes"]])
        print("steps:", [scl[(note+step*2) % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps
    print("Final melody:", melody['notes'])
    print(len(scl))

    return melody

# --------------------------------------------------------------------------------
def midiGen(filename, genome, num_bars, num_notes, num_steps, key, scale, root, bpm):
    
    # Generate a melody dictionary
    melody = melodyGen(genome, num_bars, num_notes, num_steps, key, scale, root)

    # Check if all lists are of same size
    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    # Create a single track
    mf = MIDIFile(1)

    track = 0
    channel = 0
    time = 0.0

    # Create a track and add file tempo
    mf.addTrackName(track, time, "Generated Track")
    mf.addTempo(track, time, bpm)

    # Go through velocity list and add each note with non-zero volume
    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

        time += melody["beat"][i]

    # Create a file called filename
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)

# --------------------------------------------------------------------------------
def metronome(bpm: int):
    met = Metro(time=1 / (bpm / 60.0)).play()
    t = CosTable([(0, 0), (50, 1), (200, .3), (500, 0)])
    amp = TrigEnv(met, table=t, dur=.25, mul=1)
    freq = Iter(met, choice=[660, 440, 440, 440])
    return Sine(freq=freq, mul=amp).mix(2).out()
# --------------------------------------------------------------------------------
Genome = List[int]
Population = List[Genome]

def createGenome(length) -> Genome:
    return choices([0, 1], k=length)    # returns array of length k with random 0/1 values

def generate_population(size: int, genome_length: int) -> Population:
    return [createGenome(genome_length) for _ in range(size)]

s=Server().boot()
# --------------------------------------------------------------------------------

genomeDir = []
population_fitness = []
population = []

gen_id = 1

def btnClicked():
    # Set Parameters
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    N_population = int(ui.melVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # Enable buttons
    if N_population==1:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

    elif N_population==2:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)
        
        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)
        
    elif N_population==3:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)
        
        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)
        
    elif N_population==4:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

    elif N_population==5:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

        ui.label_13.setEnabled(True)
        ui.startBtn5.setEnabled(True)
        ui.rate5.setEnabled(True)

    elif N_population==6:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

        ui.label_13.setEnabled(True)
        ui.startBtn5.setEnabled(True)
        ui.rate5.setEnabled(True)

        ui.label_14.setEnabled(True)
        ui.startBtn6.setEnabled(True)
        ui.rate6.setEnabled(True)

    elif N_population==7:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

        ui.label_13.setEnabled(True)
        ui.startBtn5.setEnabled(True)
        ui.rate5.setEnabled(True)

        ui.label_14.setEnabled(True)
        ui.startBtn6.setEnabled(True)
        ui.rate6.setEnabled(True)

        ui.label_18.setEnabled(True)
        ui.startBtn7.setEnabled(True)
        ui.rate7.setEnabled(True)

    elif N_population==8:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

        ui.label_13.setEnabled(True)
        ui.startBtn5.setEnabled(True)
        ui.rate5.setEnabled(True)

        ui.label_14.setEnabled(True)
        ui.startBtn6.setEnabled(True)
        ui.rate6.setEnabled(True)

        ui.label_18.setEnabled(True)
        ui.startBtn7.setEnabled(True)
        ui.rate7.setEnabled(True)

        ui.label_16.setEnabled(True)
        ui.startBtn8.setEnabled(True)
        ui.rate8.setEnabled(True)

    elif N_population==9:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)

        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

        ui.label_13.setEnabled(True)
        ui.startBtn5.setEnabled(True)
        ui.rate5.setEnabled(True)

        ui.label_14.setEnabled(True)
        ui.startBtn6.setEnabled(True)
        ui.rate6.setEnabled(True)

        ui.label_18.setEnabled(True)
        ui.startBtn7.setEnabled(True)
        ui.rate7.setEnabled(True)

        ui.label_16.setEnabled(True)
        ui.startBtn8.setEnabled(True)
        ui.rate8.setEnabled(True)

        ui.label_17.setEnabled(True)
        ui.startBtn9.setEnabled(True)
        ui.rate9.setEnabled(True)

    elif N_population==10:
        ui.label_10.setEnabled(True)
        ui.startBtn1.setEnabled(True)
        ui.rate1.setEnabled(True)
       
        ui.label_11.setEnabled(True)
        ui.startBtn2.setEnabled(True)
        ui.rate2.setEnabled(True)

        ui.label_12.setEnabled(True)
        ui.startBtn3.setEnabled(True)
        ui.rate3.setEnabled(True)

        ui.label_15.setEnabled(True)
        ui.startBtn4.setEnabled(True)
        ui.rate4.setEnabled(True)

        ui.label_13.setEnabled(True)
        ui.startBtn5.setEnabled(True)
        ui.rate5.setEnabled(True)

        ui.label_14.setEnabled(True)
        ui.startBtn6.setEnabled(True)
        ui.rate6.setEnabled(True)

        ui.label_18.setEnabled(True)
        ui.startBtn7.setEnabled(True)
        ui.rate7.setEnabled(True)

        ui.label_16.setEnabled(True)
        ui.startBtn8.setEnabled(True)
        ui.rate8.setEnabled(True)

        ui.label_17.setEnabled(True)
        ui.startBtn9.setEnabled(True)
        ui.rate9.setEnabled(True)

        ui.label_19.setEnabled(True)
        ui.startBtn10.setEnabled(True)
        ui.rate10.setEnabled(True)

    print("\nParameters -")
    print("Bars:", bars)
    print("Notes:", notes)
    print("BPM:", bpm)
    print("Key:", key)
    print("Scale:", scale)
    print("Root:", root)
    print("Step:", step)

    for i in range(N_population):
        j=i+1

        genome = createGenome(bars*notes*bits_per_note)
        population.append(genome)
        
        midiGen(f"C:\\Users\\udaya\\Documents\\000_BE_PROJECT\\GUI_Test3\\MIDI\\Generation{gen_id}\\melody{j}.mid", genome, bars, notes, step, key, scale, root, bpm)
    print(population)
# --------------------------------------------------------------------------------

def newGenBtnClicked():
    global population, gen_id

    current_gen = int(ui.gen_num.text())
    ui.gen_num.setText(str(current_gen+1))

    random.shuffle(population)

    ui.rate1.setValue(3)
    ui.rate2.setValue(3)
    ui.rate3.setValue(3)
    ui.rate4.setValue(3)
    ui.rate5.setValue(3)
    ui.rate6.setValue(3)
    ui.rate7.setValue(3)
    ui.rate8.setValue(3)
    ui.rate9.setValue(3)
    ui.rate10.setValue(3)

    population_fitness.clear()
    # Create population_fitness list as [(genome1, score1)..]
    if len(population)==1:
        population_fitness.append((population[0], ui.rate1.value()))
    elif len(population)==2:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
    elif len(population)==3:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
    elif len(population)==4:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
    elif len(population)==5:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
        population_fitness.append((population[4], ui.rate5.value()))
    elif len(population)==6:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
        population_fitness.append((population[4], ui.rate5.value()))
        population_fitness.append((population[5], ui.rate6.value()))
    elif len(population)==7:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
        population_fitness.append((population[4], ui.rate5.value()))
        population_fitness.append((population[5], ui.rate6.value()))
        population_fitness.append((population[6], ui.rate7.value()))
    elif len(population)==8:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
        population_fitness.append((population[4], ui.rate5.value()))
        population_fitness.append((population[5], ui.rate6.value()))
        population_fitness.append((population[6], ui.rate7.value()))
        population_fitness.append((population[7], ui.rate8.value()))
    elif len(population)==9:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
        population_fitness.append((population[4], ui.rate5.value()))
        population_fitness.append((population[5], ui.rate6.value()))
        population_fitness.append((population[6], ui.rate7.value()))
        population_fitness.append((population[7], ui.rate8.value()))
        population_fitness.append((population[8], ui.rate9.value()))
    elif len(population)==10:
        population_fitness.append((population[0], ui.rate1.value()))
        population_fitness.append((population[1], ui.rate2.value()))
        population_fitness.append((population[2], ui.rate3.value()))
        population_fitness.append((population[3], ui.rate4.value()))
        population_fitness.append((population[4], ui.rate5.value()))
        population_fitness.append((population[5], ui.rate6.value()))
        population_fitness.append((population[6], ui.rate7.value()))
        population_fitness.append((population[7], ui.rate8.value()))
        population_fitness.append((population[8], ui.rate9.value()))
        population_fitness.append((population[9], ui.rate10.value()))

    sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)
    next_generation = population[0:2]

    for j in range(int(len(population)/2)-1):

        # Go through <gen1, score1> in population_fitness and if genome
        # matches the highest score, return the next genome

        def fitness_lookup(genome):
            for e in population_fitness:
                if e[0] == genome:
                    return e[1]
            return 0
        
        parents = selection_pair(population, fitness_lookup)
        offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
        offspring_a = mutation(offspring_a, num=ui.mutVal.value(), probability=ui.mprobVal.value())
        offspring_b = mutation(offspring_b, num=ui.mutVal.value(), probability=ui.mprobVal.value())
        next_generation += [offspring_a, offspring_b]
    
    population = next_generation

    # ------------------------------------------
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    N_population = int(ui.melVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    gen_id += 1

    for i in range(len(population)):
        j=i+1
        
        midiGen(f"C:\\Users\\udaya\\Documents\\000_BE_PROJECT\\GUI_Test3\\MIDI\\Generation{gen_id}\\melody{j}.mid", population[i], bars, notes, step, key, scale, root, bpm)

# --------------------------------------------------------------------------------

def startB1Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    m=metronome(bpm)

    events=eventGen(population[0], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB2Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[1], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB3Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[2], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB4Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[3], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB5Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[4], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB6Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[5], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB7Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[6], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB8Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[7], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB9Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[8], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

def startB10Clicked(events):
    bars = int(ui.barVal.value())
    notes = int(ui.noteVal.value())
    bpm = int(ui.bpmVal.value())

    key = ui.keyVal.currentText()
    scale = ui.scaleVal.currentText().lower()
    root = int(ui.rootVal.value())
    step = int(ui.stepVal.value())

    if scale=='minor':
        scale="minorM"
    elif scale=='major blues':
        scale="majorBlues"
    elif scale=='minor blues':
        scale="minorBlues"

    # ----------------------------------------------------------------------
    events=eventGen(population[9], bars, notes, step, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    
    time.sleep(20)

    for e in events:
        e.stop()

# -------------------------------------------
# Connect button to a function
ui.genBtn.clicked.connect(btnClicked)
ui.ngenBtn.clicked.connect(newGenBtnClicked)

ui.startBtn1.clicked.connect(startB1Clicked)
ui.startBtn2.clicked.connect(startB2Clicked)
ui.startBtn3.clicked.connect(startB3Clicked)
ui.startBtn4.clicked.connect(startB4Clicked)
ui.startBtn5.clicked.connect(startB5Clicked)
ui.startBtn6.clicked.connect(startB6Clicked)
ui.startBtn7.clicked.connect(startB7Clicked)
ui.startBtn8.clicked.connect(startB8Clicked)
ui.startBtn9.clicked.connect(startB9Clicked)
ui.startBtn10.clicked.connect(startB10Clicked)
# -------------------------------------------
win.show()
app.exec()