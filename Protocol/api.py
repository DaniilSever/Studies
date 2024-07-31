from deps import AapiUC

def get(uc: AapiUC):
    uc.get_item()

def clean(uc: AapiUC):
    uc.clean_table()

def delet(uc: AapiUC):
    uc.del_item()
