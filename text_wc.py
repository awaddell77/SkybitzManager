import os
def text_wc(x,output='listoutput.txt', v = 0):#takes list writes to text
    if '.' not in output:
        raise TypeError("No file extension detected.")
    n_l = x
    name = output
    num = 0
    while(file_present(output)):
        num += 1
        fname_extension = output.split('.')
        fname, extension = fname_extension[0], fname_extension[1]
        output = fname + str(num) + "." + extension


    
    with open(name, 'w') as wf:
        for i in range(0, len(n_l)):
            if v:
                print(n_l[i])
                new = n_l[i]
                wf.writelines(new)

            else:
                new = n_l[i]
                wf.writelines(new)
    print("%s saved to %s" % (output, output))
    return True

def file_present(x):
    #only checks current working directory
    full_path = os.getcwd() + '\\' + x
    if os.path.exists(full_path):
        return True
    if not os.path.exists(full_path):
        return False
