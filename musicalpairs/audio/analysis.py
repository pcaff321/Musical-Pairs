import pymysql as db
j_list = []
k_list = []
connection = db.connect(host=""
                        user=""
                        password=""
                        database="")
cursor = db.DictCursor()

def sort(): # sort the data into groups based on the variables at play
    with connection:
        with cursor:
            data = """SELECT var, awnsers FROM userdata"""
            for row in data:
                if data[0] == 'j':
                    j_list += data[1]
                elif data[0] == "k":
                    k_list += data[1]


def analyse():
    for i in range(len(k_list)):
        if k_list[i] = 'y':
            ky += 1
        elif k_list[i] = 'n':
            kn += 1
    k_pct = (ky / kn) * 100

    for i in range(len(j_list)):
        if j_list[i] = 'y':
            jy += 1
        elif j_list[i] = 'n':
            jn += 1
    j_pct = (jy / jn) * 100

    if k_pct > j_pct:
        return "results suggest that the hypothesis is correct"
    else:
        return "results oppose the hypothesis"
        
def graph():
    return