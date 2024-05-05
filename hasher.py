strs = 'abcdefghijklmnopqrstuvwxyz' 
def hasher(password):
    shift=1
    data = []
    for i in password:                     
        if i.strip() and i in strs:        
            data.append(strs[(strs.index(i) + shift) % 26])    
        else:
            data.append(i)          
    output = ''.join(data)
    return output