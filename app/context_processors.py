from datetime import datetime
 
def inject_now():
    """Inject the current time into all templates"""
    return {'now': datetime.utcnow()} 