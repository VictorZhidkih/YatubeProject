import datetime 

def year (request):
    dt = datetime.date.today().year
    return {
        'year' : dt
    }