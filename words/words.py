# Working memory removal task for letter stimuli, as described in the study:

# Singh, K. A., Gignac, G. E., Brydges, C. R., & Ecker, U. K. (2018). Working

# memory capacity mediates the relationship between removal and fluid

# intelligence. Journal of Memory and Language, 101, 18-36.

# This script was written using python 3.7 for windows by Jeremy Simon.

# Please ensure the file wrapper.py is in the same directory as the main script

# This program creates two result csv files in the same directory as the script

# the first is named (participant id)upd.csv. It lists every update trial

# along with the block (called trial in original literature), reaction time,

# and time between cue and update (the variable differentiating conditions)

# the other is name one named (participant id)mem.csv. It records the accuracy

# of each frame test, the block number, and the reaction time.

import pygame, random, string, numpy, csv, os, wrapper, configparser
from pygame.locals import *

win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIN_WIDTH, WIN_HEIGHT = pygame.display.Info().current_w, \
 pygame.display.Info().current_h
confg = configparser.ConfigParser()
confg.read('confg_words.cfg')

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# variables which might be useful to adjust:
BLOCKS = int(confg.get('var', 'blocks'))
PRACTICE_BLOCKS = int(confg.get('var', 'practice_blocks'))
UPDATES = int(confg.get('var', 'updates'))
STIM_DELAY = int(confg.get('var', 'stim_delay'))
CROSS_DELAY = int(confg.get('var', 'cross_delay'))
RECT_SIDE_DIVISOR = int(confg.get('var', 'rect_side_divisor'))
RECT_SIDE = WIN_HEIGHT/RECT_SIDE_DIVISOR
FONT_SIZE = int(confg.get('var', 'font_size'))

# set the positions of words and frames:
FIRST_RECT = (WIN_WIDTH/2-RECT_SIDE/2, WIN_HEIGHT/2-RECT_SIDE/2)

RECTS_POS = [(FIRST_RECT[0]-1.5*RECT_SIDE, FIRST_RECT[1]),
            (FIRST_RECT[0], FIRST_RECT[1]),
            (FIRST_RECT[0]+1.5*RECT_SIDE, FIRST_RECT[1])]

WORD_POSITIONS = [(FIRST_RECT[0]-RECT_SIDE, FIRST_RECT[1]+.5*RECT_SIDE),
    (WIN_WIDTH/2,WIN_HEIGHT/2),
    (FIRST_RECT[0]+2*RECT_SIDE, FIRST_RECT[1]+.5*RECT_SIDE)]

# create the lists which store testing results:
accuracies = [[] for block in range(BLOCKS)]
test_rts = [[] for block in range(BLOCKS)]
stimuli = [[] for block in range(BLOCKS)]
responses = [[] for block in range(BLOCKS)]

# messages that will be displayed to participant
pid_request = confg.get('message', 'pid_request')
instructions = confg.get('message', 'instructions')
instructions2 = confg.get('message', 'instructions2pt1')+" "+ \
                str(PRACTICE_BLOCKS)+" "+confg.get('message', 
                   'instructions2pt2')
instructions3 = confg.get('message', 'instructions3')
timeout_warning = confg.get('message', 'timeout_warning')
testing_phase_instr = confg.get('message', 'testing_phase_instr')
exit_message = confg.get('message', 'exit_message')

word_file = open("wordlist.txt", "r")
words = word_file.read().splitlines()
word_file.close()


def get_start_words():
    """
    This function generates three random starting word stimuli which will be 
    
    updated one by one at each trial. 
    
    Returns:
    sample - A list of word stimuli.
    """
    
    permed = numpy.random.permutation(words)
    sample = permed[0:3]  # take three samples from the permuted list
    return sample


def draw_frames():
    """
    This function blanks out the window and draws three frames.
    """
    win.fill(WHITE)
    pygame.draw.rect(win, BLACK, (RECTS_POS[0][0], RECTS_POS[0][1],
                                  RECT_SIDE, RECT_SIDE), 1)
    pygame.draw.rect(win, BLACK, (RECTS_POS[1][0], RECTS_POS[1][1],
                                  RECT_SIDE, RECT_SIDE), 1)
    pygame.draw.rect(win, BLACK, (RECTS_POS[2][0], RECTS_POS[2][1],
                                  RECT_SIDE, RECT_SIDE), 1)


def save_and_quit(file):
    """
    This function exits the program, closes the update results file and
    
    saves a testing results file to csv. 
    
    Parameters:
    file - An open updating results file
    """
    
    file.close
    file = open(filename+'mem.csv','w')  # open file for testing results
    file.write('Block: Accuracy: RT: Response: Stimulus:\n')

    # write accuracies and reaction times for each frame in each block
    for block in range(len(accuracies)):
        for frame in range(len(accuracies[block])):
            file.write(str(block+1)+' '+str(accuracies[block][frame])+ \
                       ' '+str(test_rts[block][frame])+' '+ \
                       str(responses[block][frame])+' '+ \
                       str(stimuli[block][frame])+'\n')
    file.close()
    pygame.quit()
    

def wait_for_space():
    """
    This function loops continuously until the space key is pressed.
    """
    
    pygame.event.clear()
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                loop = False
                

def print_instructions(message):
    """
    This prints a wrapped message to the screen and waits for a key press
    
    Parameters:
    message - String to be displayed to the participant
    """
    
    inst_font = pygame.font.SysFont('Arial', 40)
    win.fill(WHITE)
    wrapper.renderTextCenteredAt(message, inst_font, BLACK, WIN_WIDTH/2,
                                 WIN_HEIGHT/4, win, WIN_WIDTH*0.75)
    pygame.display.update()
    wait_for_space()


def get_pid(message):
    """
    This function asks the participant for their ID and opens a file starting
    
    with the string returned.
    
    Parameters:
    message - A string requesting the participant ID from the participant
    
    Returns:
    filename, f - name string, file to record the updating steps to csv
    """

    while True:
        kwargs = {'message': message}
        pid = get_user_input(False, **kwargs)

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        filename = pid

        if not os.path.isfile(filename+'upd.csv'):
            f = open(filename+'upd.csv','w')
            f.write('Block: Step: RT: Delay:\n')
            return filename, f
            break

        message = 'PID already taken. Please try again:'
        
        
def display_starting_words():
    """
    This function retrieves starting word stimuli, prints them in their 
    
    associated frames, and waits for a specified interval.
    
    Returns:
    sample - list of starting word stimuli
    """
    
    win.fill(WHITE)
    pygame.event.clear()
    surface = font_obj.render('+', False, BLACK)
    win.blit(surface, surface.get_rect(center = WORD_POSITIONS[1]))
    pygame.display.update()
    pygame.time.wait(CROSS_DELAY)

    sample = get_start_words()
    draw_frames()

    for frame in range(3):
        surface = font_obj.render(sample[frame].lower(), False, BLACK)
        win.blit(surface, surface.get_rect(center = WORD_POSITIONS[frame]))

    pygame.display.update()
    pygame.time.wait(STIM_DELAY)  # give participant time to remember words

    draw_frames()
    pygame.display.update()
    
    return sample


def update_words(sample):
    """
    This function randomly updates one of the three word stimuli and
    
    prints it to screen. The waiting condition is randomly determined for
    
    each update.
    
    Parameters:
    sample - list of word stimuli
    
    Returns:
    delay - a waiting time interval which dictates the experimental condition
    """
    
    draw_frames()
    loop = True

    # find a word to use as update
    while loop:
        loop = False
        number = random.randint(1,len(words)-1)

        for i in sample:  # make sure update doesn't match any current words
            if i == words[number]:
                loop = True

    update_frame = random.randint(0, 2)
    pygame.draw.rect(win, RED, (RECTS_POS[update_frame][0], 
                                RECTS_POS[update_frame][1], 
                                RECT_SIDE, RECT_SIDE), 2)

    first_delay = 0
    delay = random.choice([1500,200])

    if delay == 200:
        first_delay = 1300

    pygame.time.wait(first_delay)
    pygame.display.update()
    pygame.time.wait(delay)

    sample[update_frame] = words[number]
    surface = font_obj.render(words[number].lower(), False, BLACK)
    win.blit(surface, surface.get_rect(center=WORD_POSITIONS[update_frame]))
    
    return delay


def check_for_encoding(file, pt_response):
    """
    This function displays an update to the stimuli and waits for a key press
    
    confirm encoding of the update. Displays a timeout message after 
    
    5 seconds has passed.
    
    Parameters:
    file, pt_response - an open update results file, boolean stating whether
    
    or not the participant has yet responded
    
    Returns:
    to_update, pt_response, rt - int determining if this is the last trial
    
    in block, boolean signifying pt has responded, reaction time for response
    """
    
    pygame.display.update()
    clock2start = pygame.time.get_ticks()  # second clock/check for timeout
    loop = True
    pygame.event.clear()
    
    while loop:
    
        if pygame.time.get_ticks() - clock2start > 4999:
            print_instructions(timeout_warning)
            to_update = 0  # ensures that block doesn't end after timeout
            rt = "NaN"
            break
    
        # record response and reaction time
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_and_quit(file)
                    break
                rt = clock.tick_busy_loop(0)  # record reaction time
                to_update = random.randint(0,9)  # 10% chance of ending block
                loop = False  # break inner loop (move onto an updating step)
                pt_response = True  # break outer loop (update not a "repeat")
    
    draw_frames()
    pygame.display.update()
    
    return to_update, pt_response, rt


def run_blocks(BLOCKS, file, practice=False):
    """
    This function calls the last three functions to display starting stimuli,
    
    and then perform all updating steps for all blocks. After all trials 
    
    are completed for each block it prints additional instructions and 
    
    triggers the testing phase.
    
    Parameters:
    BLOCKS, file, practice - number of (practice or testing) blocks, 
    
    an open update results file, boolean stating whether these are practice
    
    blocks or the main experiment
    """
    
    for block in range(BLOCKS):
        
        sample = display_starting_words()

        for update in range(UPDATES):
            
            pt_response = False  # we will repeat this update if pt times out
            while not pt_response:  # loop ends only when pt indicates encoding

                delay = update_words(sample)
                to_update, pt_response, rt = check_for_encoding(file, 
                                                                pt_response)

            if not practice:
                file.write(str(block+1)+" "+str(update+1)+" "+ \
                           str(rt)+" "+str(delay)+"\n")
    
            if to_update == 9:
                break
    
        if practice and block == 0:
            print_instructions(testing_phase_instr)
    
        testing_phase(practice, sample, block)


def testing_phase(practice, sample, block):
    """
    This function calls the last three functions to display starting stimuli,
    
    and then perform all updating steps for all blocks. After all trials 
    
    are completed for each block it prints additional instructions and 
    
    triggers the testing phase.
    
    Parameters:
    BLOCKS, file, practice - number of (practice or testing) blocks, 
    
    an open update results file, boolean stating whether these are practice
    
    blocks or the main experiment
    """
    
    draw_frames()
    pygame.display.update()
    question_mark = font_obj.render('?', False, BLACK)

    frameorder = numpy.random.permutation([0,1,2])
    pygame.time.wait(500)

    for frame in frameorder:

        win.blit(question_mark,
                 question_mark.get_rect(center=WORD_POSITIONS[frame]))

        pygame.display.update()
        clock.tick_busy_loop(0)

        kwargs = {'frame': frame, 'sample': sample}

        response, correct, rt = get_user_input(True, **kwargs)

        if not practice:
            accuracies[block].append(correct)
            test_rts[block].append(rt)
            responses[block].append(response)
            stimuli[block].append(sample[frame])



def get_user_input(test_phase, **kwargs):
    """
    This function retrieves a string entered by the user as either a
    
    participant ID or a testing step. After each letter it calls a second
    
    function to draw the entry to the screen.
    
    Parameters:
    test_phase, **kwargs - boolean stating whether this is the test phase
    
    or PID entry, dictionary containing either stimuli and test frame
    
    (for test phase) or instructions (PID entry)
    
    Returns:
    response, correct, rt - participant response, response accuracy, and
    
    reaction time if testing phase
    
    p_input - input string if PID entry phase
    """
    
    key = ''
    p_input = ''
    correct = False
    response = []
    loop = True
    pygame.event.clear()

    while loop:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.unicode.isalpha() or event.unicode.isnumeric():
                    key += event.unicode
                    p_input = p_input + key[-1]
                    if test_phase:
                        if len(p_input) > 2:
                            loop = False
                            response = p_input
                            rt = clock.tick_busy_loop(0)

                            if rt > 4999:
                                rt = "NaN"

                            if response[:3].lower() == \
                            kwargs['sample'][kwargs['frame']][:3].lower():
                                correct = True
                elif event.key == K_BACKSPACE:
                    key = key[:-1]
                    p_input = p_input[:-1]
                elif not test_phase and event.key == \
                    K_RETURN and len(p_input) > 0:
                    key = ''
                    loop = False
                elif event.key == pygame.K_ESCAPE:
                    save_and_quit(f)
                    break
            elif event.type == QUIT:
                loop = False

        draw_user_input(key, test_phase, **kwargs)

    if test_phase:
        return response, correct, rt
    else:
        return p_input


def draw_user_input(key, test_phase, **kwargs):
    """
    This function draws a string to the screen letter by letter as 
    
    the participant enters it.
    
    Parameters:
    key, test_phase, **kwargs - last key press, boolean stating whether this 
    
    is the test phase or PID entry, dictionary containing either stimuli 
    
    and test frame (for test phase) or instructions (PID entry)
    """
    
    win.fill(WHITE)
    pid_surface = font_obj.render(key, True, BLACK)
    rect = pid_surface.get_rect()

    if test_phase:
        question_mark = font_obj.render('?', False, BLACK)
        rect.centerx = win.get_rect().centerx
        rect.centery = win.get_rect().centery + 200
        draw_frames()
        win.blit(question_mark,
                 question_mark.get_rect(center=WORD_POSITIONS[kwargs['frame']]))
    else:
        message_surface = font_obj.render(kwargs['message'], False, BLACK)
        win.blit(message_surface, 
                 message_surface.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2.5)))
        rect.center = win.get_rect().center

    win.blit(pid_surface, rect)
    pygame.display.update()


def initialize_pygame():
    """
    This function initializes the pygame module to open a window to draw
    
    stimuli.
    
    Returns:     
    clock, font_obj - clock object to record reaction time, font object 
    
    to render text to screen
    """
    
    pygame.init()                 
    pygame.display.set_caption("Working Memory Removal") 
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    font_obj = pygame.font.SysFont('Arial', FONT_SIZE)
    
    return clock, font_obj
    
def run_experiment():
    """
    This function prints instructions to the screen in the appropriate order
    
    and calls the run_blocks function to run the experiment, once for the
    
    practice blocks and once for the main blocks
    """
    
    print_instructions(instructions)
    print_instructions(instructions2)
    run_blocks(PRACTICE_BLOCKS, f, True)  
    print_instructions(instructions3)
    run_blocks(BLOCKS, f)
    print_instructions(exit_message)
    save_and_quit(f)
   
clock, font_obj = initialize_pygame()
filename, f = get_pid(pid_request)                                     #get PID and make sure it isn't already taken
run_experiment()

#pyinstaller.exe --onefile main.py
# cd documents/python
# py -3 main.py
