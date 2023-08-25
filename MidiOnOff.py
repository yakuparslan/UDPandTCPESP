from mido import MidiFile
import os
bpm = 120
millisecond_per_tick = bpm/60/16*1000

mid = MidiFile('FasterTestStandard.mid', clip=True)


import pandas as pd

df = pd.DataFrame(columns=['Switch','Note','Time'])


for msg in mid.tracks[0]:
    if(msg.type=='note_on' or msg.type=='note_off'):
        list_row = [msg.type, msg.note,msg.time]
        
        df.loc[len(df)] = list_row
        

df['cum_sum'] = df['Time'].cumsum()



df['time_ms'] = df['cum_sum']/24*millisecond_per_tick
df['time_ms'] = df['time_ms'].astype(int)
df = df[['Switch','Note','time_ms']]
df.rename(columns = {'time_ms':'time','Note':'Notes'}, inplace = True)

print(df)

df_on = df[df.Switch=='note_on']
df_off = df[df.Switch=='note_off']
first_line  = '#ifndef NOTES_H__'
second_line = '#define NOTES_H__'
array_line = 'const int array_length = sizeof(notes_on)/sizeof(notes_on[0]);'
last_line = '#endif'

for note in df_on['Notes'].unique():
    cpp_arrays = []
    note_folder = str(note)
    cpp_arrays.append(first_line)
    cpp_arrays.append(second_line)
    note_timeline_on = df_on[df_on['Notes'] == note]['time'].tolist()
    cpp_array = "const int notes_on"+ "[" + str(len(note_timeline_on)) + "] = {" + ", ".join(str(t) for t in note_timeline_on) + "};"
    cpp_arrays.append(cpp_array)
    note_timeline_off = df_off[df_off['Notes'] == note]['time'].tolist()
    cpp_array =  "const int notes_off"+ "[" + str(len(note_timeline_off)) + "] = {" + ", ".join(str(t) for t in note_timeline_off) + "};"
    cpp_arrays.append(cpp_array)
    cpp_arrays.append(array_line)
    cpp_arrays.append(last_line)


  # Create folder for the note if it doesn't exist
    if not os.path.exists(note_folder):
        os.makedirs(note_folder)

    # Create Notes.h file inside the note folder and write the C++ array
    with open(os.path.join(note_folder, "Notes.h"), "w") as file:
        for cpp_array in cpp_arrays:
            file.write(cpp_array + "\n")
             
    



   