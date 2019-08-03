import sys

sys.path.append('../')
sys.path.append('./')

from fixtures.router import router

@router.resource('/resource-b')
class ResourceB():
    pass