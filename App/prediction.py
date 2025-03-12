import random

def tracker():
    # turn on cam before runniing
    
    
    
    emotion = ['Happy' , 'anger' ,  'neutral' ]
    k =  random.choice(emotion)
    
    gaze =  random.randint(1,10)
    
    e_device =  random.choice([True , False])
    
    return [k , gaze , e_device ]


