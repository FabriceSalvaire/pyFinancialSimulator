# root = {}
# parent_level = None
# current_level = 1
# current_level = root
with open('plan-comptable-français.txt') as f:
    for line in f:
        line = line.strip()
        if line:
            if line.startswith('Classe'):
                code, name = [x.strip() for x in line[7:].split(':')]
            else:
                l = line.find('-')
                code = line[:l].strip()
                name = line[l+1:].strip()
            item_level = len(code)
            # print(item_level, code, name)
            print('{:6} | {}'.format(code, name))
            # if item_level == current_level:
            #     current_level[code] = name
            # elif item_level >= current_level:
            #     parent_level = current_level
            #     current_level = {}
